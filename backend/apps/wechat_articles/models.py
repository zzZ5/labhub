import hashlib
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from django.conf import settings
from django.db import models
from django.utils import timezone


TRACKING_QUERY_KEYS = {
    "ascene",
    "clicktime",
    "enterid",
    "exportkey",
    "from",
    "scene",
    "sessionid",
    "subscene",
}


def canonicalize_article_url(value):
    value = str(value or "").strip()
    if not value:
        return ""
    parts = urlsplit(value)
    query = [
        (key, item)
        for key, item in parse_qsl(parts.query, keep_blank_values=True)
        if key.lower() not in TRACKING_QUERY_KEYS
    ]
    return urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            parts.path.rstrip("/") or "/",
            urlencode(sorted(query)),
            "",
        )
    )


def article_dedupe_key(account_id, source_guid="", source_url="", title="", published_at=None):
    identity = str(source_guid or "").strip() or canonicalize_article_url(source_url)
    if not identity:
        published = published_at.isoformat() if published_at else ""
        identity = f"{str(title or '').strip()}|{published}"
    return hashlib.sha256(f"{account_id}|{identity}".encode("utf-8")).hexdigest()


class WechatAccount(models.Model):
    class SourceType(models.TextChoices):
        RSS = "rss", "RSS"
        JSON_API = "json_api", "开放接口"
        MANUAL = "manual", "仅手动录入"

    name = models.CharField("公众号名称", max_length=120)
    description = models.CharField("简介", max_length=300, blank=True)
    source_type = models.CharField("同步方式", max_length=20, choices=SourceType.choices, default=SourceType.MANUAL)
    source_url = models.URLField("RSS 或接口地址", max_length=1000, blank=True)
    api_token_env = models.CharField(
        "接口令牌环境变量",
        max_length=120,
        blank=True,
        help_text="如开放接口需要 Bearer Token，请填写服务器环境变量名称，不要在此填写令牌本身。",
    )
    is_active = models.BooleanField("启用", default=True)
    sort_order = models.PositiveIntegerField("排序", default=0)
    last_sync_attempt_at = models.DateTimeField("最后同步尝试", null=True, blank=True)
    last_sync_success_at = models.DateTimeField("最后同步成功", null=True, blank=True)
    last_sync_error = models.TextField("最后同步错误", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "公众号"
        verbose_name_plural = "公众号"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class WechatArticle(models.Model):
    account = models.ForeignKey(WechatAccount, on_delete=models.CASCADE, related_name="articles", verbose_name="公众号")
    title = models.CharField("文章标题", max_length=300)
    summary = models.TextField("简短摘要", blank=True)
    cover_url = models.URLField("封面图片地址", max_length=1500, blank=True)
    source_url = models.URLField("微信原文链接", max_length=1500)
    source_guid = models.CharField("来源文章标识", max_length=500, blank=True)
    dedupe_key = models.CharField("去重标识", max_length=64, unique=True, editable=False)
    published_at = models.DateTimeField("发布时间")
    is_visible = models.BooleanField("公开展示", default=True)
    is_manual = models.BooleanField("手动录入", default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_wechat_articles",
        verbose_name="录入人",
        null=True,
        blank=True,
    )
    synced_at = models.DateTimeField("同步时间", null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "公众号文章"
        verbose_name_plural = "公众号文章"
        ordering = ["-published_at", "-id"]
        indexes = [
            models.Index(fields=["-published_at"], name="wechat_pub_at_idx"),
            models.Index(fields=["account", "-published_at"], name="wechat_acc_pub_idx"),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.dedupe_key = article_dedupe_key(
            self.account_id,
            source_guid=self.source_guid,
            source_url=self.source_url,
            title=self.title,
            published_at=self.published_at,
        )
        if not self.synced_at:
            self.synced_at = timezone.now()
        super().save(*args, **kwargs)

