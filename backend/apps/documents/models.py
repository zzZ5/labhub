from django.conf import settings
from django.db import models

from apps.accounts.models import Role

from .storage import ProtectedMediaStorage


protected_storage = ProtectedMediaStorage()


class DocumentVisibility(models.TextChoices):
    PUBLIC = "public", "公开"
    MEMBERS = "members", "成员可见"
    PHD = "phd", "博士/管理员可见"
    PI = "pi", "硕博导师/管理员可见"
    CUSTOM = "custom", "指定人员可见"


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
    visibility = models.CharField("可见性", max_length=20, choices=DocumentVisibility.choices, default=DocumentVisibility.MEMBERS)

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
    current_version = models.CharField("当前版本", max_length=40, blank=True)
    visibility = models.CharField("可见性", max_length=20, choices=DocumentVisibility.choices, default=DocumentVisibility.MEMBERS)
    allow_download = models.BooleanField("允许下载", default=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="owned_documents", verbose_name="所有者", null=True, blank=True)
    maintainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="maintained_documents", verbose_name="维护人", null=True, blank=True)
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
        return self.versions.filter(is_current=True).order_by("-uploaded_at").first()


class DocumentVersion(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="versions", verbose_name="资料")
    version = models.CharField("版本号", max_length=40)
    file = models.FileField("文件", storage=protected_storage, upload_to="documents/")
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
    change_log = models.TextField("更新说明", blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="uploaded_document_versions", verbose_name="上传人", null=True, blank=True)
    uploaded_at = models.DateTimeField("上传时间", auto_now_add=True)
    file_size = models.PositiveBigIntegerField("文件大小", default=0)
    file_type = models.CharField("文件类型", max_length=100, blank=True)
    is_current = models.BooleanField("是否当前版本", default=True)

    class Meta:
        verbose_name = "资料版本"
        verbose_name_plural = "资料版本"
        unique_together = ("document", "version")
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return f"{self.document} {self.version}"

    def save(self, *args, **kwargs):
        if self.file and not self.file_size:
            self.file_size = self.file.size
        if self.file and not self.original_filename:
            self.original_filename = self.file.name.split("/")[-1]
        if self.is_current:
            DocumentVersion.objects.filter(document=self.document, is_current=True).exclude(pk=self.pk).update(is_current=False)
            self.document.current_version = self.version
            self.document.save(update_fields=["current_version", "updated_at"])
        super().save(*args, **kwargs)


class DocumentPermission(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="permissions", verbose_name="资料")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="document_permissions", verbose_name="用户", null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="document_permissions", verbose_name="角色", null=True, blank=True)
    can_view = models.BooleanField("可查看", default=True)
    can_download = models.BooleanField("可下载", default=True)
    can_edit = models.BooleanField("可编辑", default=False)
    expires_at = models.DateTimeField("过期时间", null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="created_document_permissions", verbose_name="创建人", null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "资料权限"
        verbose_name_plural = "资料权限"

    def __str__(self) -> str:
        target = self.user or self.role
        return f"{self.document} - {target}"


class DocumentDownloadLog(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="download_logs", verbose_name="资料")
    version = models.ForeignKey(DocumentVersion, on_delete=models.SET_NULL, related_name="download_logs", verbose_name="版本", null=True, blank=True)
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


class DocumentFavorite(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="favorites", verbose_name="资料")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="document_favorites", verbose_name="用户")
    created_at = models.DateTimeField("收藏时间", auto_now_add=True)

    class Meta:
        verbose_name = "资料收藏"
        verbose_name_plural = "资料收藏"
        unique_together = ("document", "user")

    def __str__(self) -> str:
        return f"{self.user} - {self.document}"
