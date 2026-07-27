from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Role, RoleCode, UserRole

from .models import WechatAccount, WechatArticle
from .services import parse_json_payload, parse_rss_payload, source_request_url, store_feed_articles


class FeedParsingTests(TestCase):
    def setUp(self):
        self.account = WechatAccount.objects.create(
            name="测试公众号",
            source_type=WechatAccount.SourceType.RSS,
            source_url="https://example.com/feed.xml",
        )

    def test_rss_is_parsed_and_duplicate_articles_are_updated(self):
        payload = b"""<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0"><channel><item>
          <guid>article-1</guid><title>Composting research</title>
          <link>https://mp.weixin.qq.com/s?__biz=test&amp;mid=1&amp;scene=1</link>
          <description><![CDATA[<p>A short <strong>summary</strong>.</p><img src="https://example.com/cover.jpg" />]]></description>
          <pubDate>Mon, 20 Jul 2026 08:00:00 +0800</pubDate>
        </item></channel></rss>"""
        articles = parse_rss_payload(payload)
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].summary, "A short summary.")
        self.assertEqual(articles[0].cover_url, "https://example.com/cover.jpg")

        first = store_feed_articles(self.account, articles)
        second = store_feed_articles(self.account, articles)
        self.assertEqual(first["created"], 1)
        self.assertEqual(second["created"], 0)
        self.assertEqual(second["updated"], 1)
        self.assertEqual(WechatArticle.objects.count(), 1)

    def test_json_api_contract(self):
        payload = b"""{"articles":[{"id":"a-1","title":"Article","url":"https://example.com/a","summary":"Summary","published_at":"2026-07-20T08:00:00+08:00"}]}"""
        articles = parse_json_payload(payload)
        self.assertEqual(articles[0].source_guid, "a-1")
        self.assertEqual(articles[0].title, "Article")

    @override_settings(WECHAT_SYNC_RSS_ITEM_LIMIT=5)
    def test_rss_request_adds_item_limit_without_replacing_existing_query(self):
        self.account.source_url = "https://example.com/feed.xml?token=abc"
        self.assertEqual(source_request_url(self.account), "https://example.com/feed.xml?token=abc&limit=5")

        self.account.source_url = "https://example.com/feed.xml?limit=2"
        self.assertEqual(source_request_url(self.account), "https://example.com/feed.xml?limit=2")


class WechatArticleApiTests(TestCase):
    def setUp(self):
        self.account = WechatAccount.objects.create(name="公众号甲")
        WechatArticle.objects.create(
            account=self.account,
            title="较新文章",
            source_url="https://example.com/new",
            summary="新摘要",
            published_at=timezone.now(),
        )
        WechatArticle.objects.create(
            account=self.account,
            title="较早文章",
            source_url="https://example.com/old",
            published_at=timezone.now() - timedelta(days=2),
        )

    def test_public_articles_are_newest_first_and_searchable(self):
        client = APIClient()
        response = client.get("/api/wechat/articles/", {"search": "较新"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "较新文章")

    @patch("apps.wechat_articles.views.sync_all_wechat_accounts.delay")
    def test_editor_can_trigger_sync(self, delay):
        user = get_user_model().objects.create_user(username="editor", password="password")
        user.profile.is_approved = True
        user.profile.save(update_fields=["is_approved", "updated_at"])
        role = Role.objects.get(code=RoleCode.EDITOR)
        UserRole.objects.create(user=user, role=role)
        client = APIClient()
        client.force_authenticate(user)
        response = client.post("/api/wechat/manage/accounts/sync-all/")
        self.assertEqual(response.status_code, 202)
        delay.assert_called_once()
