import hashlib
import json
import re
from html import unescape
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.core.cache import cache


class MetadataError(ValueError):
    pass


def normalize_doi(value):
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", str(value or "").strip(), flags=re.I)
    value = re.sub(r"^doi\s*:\s*", "", value, flags=re.I).strip().lower()
    if value and (len(value) > 250 or not re.fullmatch(r"10\.\d{4,9}/\S+", value)):
        raise MetadataError("请填写有效的 DOI，例如 10.1038/xxxxx；也可粘贴 doi.org 链接。")
    return value


def plain_text(value):
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", str(value or ""))).split())


def infer_topic(title, subjects):
    text = f"{title} {' '.join(subjects)}".lower()
    # Prefer explicit subjects over broad words such as carbon or environment.
    rules = [
        ("compost", r"\bcompost(?:ing)?\b|\bhumification\b|堆肥|腐殖化"),
        ("environment", r"microplastic|antibiotic resistance|resistance genes|methane emission|nitrous oxide|greenhouse gas|life.cycle assessment|微塑料|抗性基因|减排"),
        ("nutrients", r"nutrient recover|phosphorus recover|nitrogen recover|fertili[sz]er substitution|struvite|养分回收|磷回收|化肥替代"),
        ("soil", r"\bsoil\b|rhizosphere|cropland|土壤|根际|还田"),
        ("biomass", r"biomass|lignocellulos|anaerobic digestion|biogas|biochar|black soldier fly|生物质|木质纤维素|厌氧消化|生物炭"),
    ]
    return next((topic for topic, pattern in rules if re.search(pattern, text)), "")


def fetch_paper_metadata(doi):
    doi = normalize_doi(doi)
    if not doi:
        raise MetadataError("请先填写 DOI。")
    cache_key = "paper-metadata-v1-" + hashlib.sha256(doi.encode()).hexdigest()
    cached = cache.get(cache_key)
    if cached:
        return dict(cached)
    url = "https://api.crossref.org/works/" + quote(doi, safe="")
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "LabHub/1.0 (DOI metadata lookup)"})
    try:
        with urlopen(request, timeout=8) as response:
            raw = response.read(2 * 1024 * 1024 + 1)
        if len(raw) > 2 * 1024 * 1024:
            raise MetadataError("文献记录过大，请展开补充信息手动填写。")
        message = json.loads(raw).get("message")
        if not isinstance(message, dict):
            raise MetadataError("文献服务返回的数据不完整，请稍后重试。")
        if normalize_doi(message.get("DOI")) != doi:
            raise MetadataError("返回记录与 DOI 不一致，未自动填入。")
        title = plain_text((message.get("title") or [""])[0])
        journal = plain_text((message.get("container-title") or [""])[0])
        if not title or len(title) > 500 or len(journal) > 200:
            raise MetadataError("原标题或期刊信息缺失或过长，请展开补充信息检查。")
        authors = []
        for author in message.get("author") or []:
            name = plain_text(author.get("name") or " ".join(filter(None, [author.get("given"), author.get("family")])))
            if name:
                if len("; ".join(authors + [name])) > 980:
                    authors.append("et al.")
                    break
                authors.append(name)
        year = None
        for field in ["published-online", "published-print", "published", "issued"]:
            parts = (message.get(field) or {}).get("date-parts") or []
            if parts and parts[0] and isinstance(parts[0][0], int) and 1000 <= parts[0][0] <= 9999:
                year = parts[0][0]
                break
        result = {
            "doi": doi, "title": title, "journal": journal, "authors": "; ".join(authors),
            "year": year, "publisher_url": "https://doi.org/" + quote(doi, safe="/"),
            "topic": infer_topic(title, message.get("subject") or []),
            "metadata_source": "Crossref", "metadata_url": url,
        }
    except HTTPError as exc:
        if exc.code == 404:
            raise MetadataError("Crossref 未找到该 DOI，请检查 DOI，或展开补充信息手动填写标题。") from exc
        raise MetadataError("文献服务暂不可用，请稍后重试或手动填写标题。") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise MetadataError("获取文献信息超时或连接失败，请稍后重试或手动填写标题。") from exc
    except (TypeError, KeyError, IndexError, AttributeError, json.JSONDecodeError, UnicodeError) as exc:
        raise MetadataError("文献服务返回的数据无法识别，请稍后重试或手动填写标题。") from exc
    cache.set(cache_key, result, 24 * 60 * 60)
    return dict(result)
