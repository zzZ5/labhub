from django.conf import settings
from django.db import models

from .storage import ProtectedMediaStorage


protected_storage = ProtectedMediaStorage()


class DocumentStatus(models.TextChoices):
    DRAFT = "draft", "草稿"
    ACTIVE = "active", "有效"
    ARCHIVED = "archived", "已归档"


class DocumentCategory(models.Model):
    name = models.CharField("分类名称", max_length=100)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="children", verbose_name="父级分类", null=True, blank=True)
    slug = models.SlugField("URL 标识", max_length=120, unique=True)
    description = models.TextField("说明", blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0)

    class Meta:
        verbose_name = "资料分类"
        verbose_name_plural = "资料分类"
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


class DocumentTag(models.Model):
    name = models.CharField("标签名称", max_length=60)
    slug = models.SlugField("URL 标识", max_length=100, unique=True)

    class Meta:
        verbose_name = "资料标签"
        verbose_name_plural = "资料标签"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Document(models.Model):
    title = models.CharField("资料标题", max_length=200)
    category = models.ForeignKey(DocumentCategory, on_delete=models.SET_NULL, related_name="documents", verbose_name="分类", null=True, blank=True)
    tags = models.ManyToManyField(DocumentTag, related_name="documents", verbose_name="标签", blank=True)
    description = models.TextField("说明", blank=True)
    external_url = models.URLField("外部视频链接", max_length=500, blank=True)
    allow_download = models.BooleanField("允许下载", default=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="owned_documents", verbose_name="所有者", null=True, blank=True)
    file = models.FileField("文件", storage=protected_storage, upload_to="documents/", blank=True)
    preview_pdf = models.FileField("PDF 预览文件", storage=protected_storage, upload_to="documents/previews/", blank=True)
    preview_status = models.CharField(
        "预览状态",
        max_length=20,
        choices=[
            ("none", "无需转换"),
            ("pending", "等待生成"),
            ("ready", "已生成"),
            ("failed", "生成失败"),
        ],
        default="none",
    )
    preview_error = models.CharField("预览错误", max_length=240, blank=True)
    original_filename = models.CharField("原始文件名", max_length=255, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="uploaded_documents", verbose_name="上传人", null=True, blank=True)
    uploaded_at = models.DateTimeField("上传时间", null=True, blank=True)
    file_size = models.PositiveBigIntegerField("文件大小", default=0)
    file_type = models.CharField("文件类型", max_length=100, blank=True)
    status = models.CharField("状态", max_length=20, choices=DocumentStatus.choices, default=DocumentStatus.DRAFT)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "资料"
        verbose_name_plural = "资料"
        ordering = ["-updated_at", "title"]

    def __str__(self) -> str:
        return self.title

    @property
    def current_file(self):
        return self if self.file else None


class DocumentDownloadLog(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="download_logs", verbose_name="资料")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="document_download_logs", verbose_name="用户", null=True, blank=True)
    ip_address = models.GenericIPAddressField("IP 地址", null=True, blank=True)
    user_agent = models.TextField("User Agent", blank=True)
    downloaded_at = models.DateTimeField("下载时间", auto_now_add=True)

    class Meta:
        verbose_name = "资料下载日志"
        verbose_name_plural = "资料下载日志"
        ordering = ["-downloaded_at"]

    def __str__(self) -> str:
        return f"{self.document} - {self.user}"
