import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
from html import unescape
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .models import WechatAccount, WechatArticle, article_dedupe_key, is_wechat_article_url


IMAGE_PATTERN = re.compile(r"<img[^>]+src=[\"']([^\"']+)", re.IGNORECASE)


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        if data.strip():
            self.parts.append(data.strip())


@dataclass
class FeedArticle:
    title: str
    source_url: str
    published_at: datetime
    summary: str = ""
    cover_url: str = ""
    source_guid: str = ""


def clean_summary(value, limit=260):
    parser = TextExtractor()
    parser.feed(str(value or ""))
    text = unescape(" ".join(parser.parts))
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.;:!?，。；：！？])", r"\1", text)
    return f"{text[:limit].rstrip()}…" if len(text) > limit else text


def parse_published_at(value):
    if isinstance(value, datetime):
        parsed = value
    else:
        raw = str(value or "").strip()
        parsed = parse_datetime(raw)
        if parsed is None and raw:
            try:
                parsed = parsedate_to_datetime(raw)
            except (TypeError, ValueError, OverflowError):
                parsed = None
    if parsed is None:
        return timezone.now()
    if timezone.is_naive(parsed):
        return timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def first_text(element, paths, namespaces=None):
    for path in paths:
        node = element.find(path, namespaces or {})
        if node is not None and node.text and node.text.strip():
            return node.text.strip()
    return ""


def first_link(element, atom=False):
    if atom:
        for node in element.findall("{*}link"):
            href = str(node.attrib.get("href", "")).strip()
            relation = node.attrib.get("rel", "alternate")
            if href and relation in {"", "alternate"}:
                return href
        return ""
    return first_text(element, ["link", "{*}link"])


def preferred_article_url(link, source_guid):
    for candidate in (source_guid, link):
        if is_wechat_article_url(candidate):
            return str(candidate).strip()
    return str(link or source_guid or "").strip()


def extract_cover(element, html_content=""):
    for node in list(element):
        tag = node.tag.rsplit("}", 1)[-1].lower()
        if tag in {"thumbnail", "content"}:
            url = str(node.attrib.get("url", "")).strip()
            media_type = str(node.attrib.get("type", "")).lower()
            if url and (tag == "thumbnail" or not media_type or media_type.startswith("image/")):
                return url
        if tag == "enclosure":
            url = str(node.attrib.get("url", "")).strip()
            if url and str(node.attrib.get("type", "")).lower().startswith("image/"):
                return url
    match = IMAGE_PATTERN.search(str(html_content or ""))
    return match.group(1).strip() if match else ""


def parse_rss_payload(payload):
    root = ElementTree.fromstring(payload)
    entries = root.findall(".//item")
    atom = False
    if not entries:
        entries = root.findall(".//{*}entry")
        atom = True
    articles = []
    for entry in entries:
        title = first_text(entry, ["title", "{*}title"])
        source_link = first_link(entry, atom=atom)
        source_guid = first_text(entry, ["guid", "{*}id"])
        source_url = preferred_article_url(source_link, source_guid)
        published = first_text(entry, ["pubDate", "{*}published", "{*}updated", "date", "{*}date"])
        content = first_text(entry, ["description", "{*}summary", "{*}content", "{*}encoded"])
        if not title or not source_url:
            continue
        articles.append(
            FeedArticle(
                title=title[:300],
                source_url=source_url,
                source_guid=source_guid[:500],
                summary=clean_summary(content),
                cover_url=extract_cover(entry, content)[:1500],
                published_at=parse_published_at(published),
            )
        )
    return articles


def parse_json_payload(payload):
    data = json.loads(payload.decode("utf-8-sig"))
    if isinstance(data, dict):
        for key in ("articles", "items", "data"):
            if isinstance(data.get(key), list):
                data = data[key]
                break
    if not isinstance(data, list):
        raise ValueError("开放接口返回格式不正确，应为文章数组或包含 articles/items/data 数组的对象。")
    articles = []
    for item in data:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        source_url = str(item.get("url") or item.get("source_url") or "").strip()
        if not title or not source_url:
            continue
        articles.append(
            FeedArticle(
                title=title[:300],
                source_url=source_url,
                source_guid=str(item.get("id") or item.get("guid") or "")[:500],
                summary=clean_summary(item.get("summary") or item.get("description") or ""),
                cover_url=str(item.get("cover_image") or item.get("cover_url") or "")[:1500],
                published_at=parse_published_at(item.get("published_at") or item.get("publish_time")),
            )
        )
    return articles


def source_request_url(account):
    if account.source_type != WechatAccount.SourceType.RSS:
        return account.source_url
    parts = urlsplit(account.source_url)
    query = parse_qsl(parts.query, keep_blank_values=True)
    if not any(key == "limit" for key, _ in query):
        query.append(("limit", str(settings.WECHAT_SYNC_RSS_ITEM_LIMIT)))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def fetch_source_payload(account):
    headers = {
        "Accept": "application/rss+xml, application/atom+xml, application/xml, application/json, text/xml;q=0.9",
        "User-Agent": "LabHub-WechatFeed/1.0",
    }
    if account.api_token_env:
        token = os.environ.get(account.api_token_env, "").strip()
        if not token:
            raise ValueError(f"服务器未配置环境变量：{account.api_token_env}")
        headers["Authorization"] = f"Bearer {token}"
    request = Request(source_request_url(account), headers=headers)
    timeout = int(getattr(settings, "WECHAT_SYNC_TIMEOUT_SECONDS", 30))
    max_feed_bytes = int(getattr(settings, "WECHAT_SYNC_MAX_FEED_MB", 24)) * 1024 * 1024
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = response.read(max_feed_bytes + 1)
    except HTTPError as exc:
        raise ValueError(f"来源地址返回 HTTP {exc.code}") from exc
    except URLError as exc:
        raise ValueError(f"无法连接来源地址：{exc.reason}") from exc
    if len(payload) > max_feed_bytes:
        max_feed_mb = max_feed_bytes // (1024 * 1024)
        raise ValueError(f"来源返回内容超过 {max_feed_mb} MB，已停止处理。")
    return payload


def store_feed_articles(account, articles):
    created = 0
    updated = 0
    now = timezone.now()
    with transaction.atomic():
        for article in articles:
            key = article_dedupe_key(
                account.pk,
                source_guid=article.source_guid,
                source_url=article.source_url,
                title=article.title,
                published_at=article.published_at,
            )
            _, was_created = WechatArticle.objects.update_or_create(
                dedupe_key=key,
                defaults={
                    "account": account,
                    "title": article.title,
                    "summary": article.summary,
                    "cover_url": article.cover_url,
                    "source_url": article.source_url,
                    "source_guid": article.source_guid,
                    "published_at": article.published_at,
                    "is_manual": False,
                    "synced_at": now,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1
    return {"created": created, "updated": updated, "total": len(articles)}


def sync_wechat_account(account):
    if account.source_type == WechatAccount.SourceType.MANUAL:
        raise ValueError("该公众号设置为仅手动录入，无需同步。")
    if not account.source_url:
        raise ValueError("尚未填写 RSS 或开放接口地址。")
    attempt_time = timezone.now()
    WechatAccount.objects.filter(pk=account.pk).update(last_sync_attempt_at=attempt_time, last_sync_error="")
    try:
        payload = fetch_source_payload(account)
        if account.source_type == WechatAccount.SourceType.JSON_API:
            articles = parse_json_payload(payload)
        else:
            articles = parse_rss_payload(payload)
        result = store_feed_articles(account, articles)
    except Exception as exc:
        WechatAccount.objects.filter(pk=account.pk).update(
            last_sync_attempt_at=attempt_time,
            last_sync_error=str(exc)[:2000],
        )
        raise
    success_time = timezone.now()
    WechatAccount.objects.filter(pk=account.pk).update(
        last_sync_attempt_at=attempt_time,
        last_sync_success_at=success_time,
        last_sync_error="",
    )
    result["account_id"] = account.pk
    result["account_name"] = account.name
    return result
