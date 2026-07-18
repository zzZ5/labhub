from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


def is_bilibili_host(hostname: str) -> bool:
    hostname = hostname.lower()
    return hostname in {"b23.tv", "www.b23.tv", "bilibili.com"} or hostname.endswith(".bilibili.com")


class BilibiliRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not is_bilibili_host(urlsplit(newurl).hostname or ""):
            raise HTTPError(newurl, code, "Blocked non-Bilibili redirect", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def open_bilibili_url(request, timeout):
    return build_opener(BilibiliRedirectHandler()).open(request, timeout=timeout)


def resolve_bilibili_short_url(value: str) -> str:
    """Resolve b23.tv links without allowing arbitrary server-side requests."""
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or (parsed.hostname or "").lower() not in {"b23.tv", "www.b23.tv"}:
        return value

    for method in ("HEAD", "GET"):
        request = Request(
            value,
            method=method,
            headers={"User-Agent": "Mozilla/5.0 LabHub video resolver"},
        )
        try:
            with open_bilibili_url(request, timeout=4) as response:
                resolved = response.geturl()
        except (HTTPError, URLError, OSError, TimeoutError, ValueError):
            continue
        target = urlsplit(resolved)
        hostname = (target.hostname or "").lower()
        if target.scheme in {"http", "https"} and is_bilibili_host(hostname) and hostname not in {"b23.tv", "www.b23.tv"}:
            return resolved
    return value
