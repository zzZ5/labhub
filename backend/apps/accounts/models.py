from django.conf import settings
from django.db import models
from django.utils import timezone


class RoleCode(models.TextChoices):
    MEMBER = "member", "课题组成员"
    MASTER = "master", "硕士生"
    PHD = "phd", "博士生"
    UNDERGRADUATE = "undergraduate", "本科生"
    POSTDOC = "postdoc", "博士后"
    OTHER = "other", "其他"
    INSTRUMENT_MANAGER = "instrument_manager", "仪器管理员"
    DOCUMENT_MANAGER = "document_manager", "资料管理员"
    EDITOR = "editor", "网站编辑"
    PI = "pi", "硕博导师"
    ADMIN = "admin", "系统管理员"


class UserProfile(models.Model):
    class RoleType(models.TextChoices):
        PENDING = "pending", "注册待审核用户"
        MEMBER = "member", "课题组成员"
        MASTER = "master", "硕士生"
        PHD = "phd", "博士生"
        UNDERGRADUATE = "undergraduate", "本科生"
        POSTDOC = "postdoc", "博士后"
        OTHER = "other", "其他"
        INSTRUMENT_MANAGER = "instrument_manager", "仪器管理员"
        DOCUMENT_MANAGER = "document_manager", "资料管理员"
        EDITOR = "editor", "网站编辑"
        PI = "pi", "硕博导师"
        ADMIN = "admin", "系统管理员"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile", verbose_name="用户")
    real_name = models.CharField("真实姓名", max_length=80, blank=True)
    avatar = models.ImageField("头像", upload_to="avatars/", blank=True)
    phone = models.CharField("手机号", max_length=30, blank=True)
    role_type = models.CharField("主角色", max_length=32, choices=RoleType.choices, default=RoleType.PENDING)
    bio = models.TextField("个人简介", blank=True)
    is_approved = models.BooleanField("是否审核通过", default=False)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_profiles",
        verbose_name="审核人",
        null=True,
        blank=True,
    )
    approved_at = models.DateTimeField("审核时间", null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "用户资料"
        verbose_name_plural = "用户资料"

    def __str__(self) -> str:
        return self.real_name or self.user.get_username()

    def approve(self, approved_by):
        self.is_approved = True
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        self.save(update_fields=["is_approved", "approved_by", "approved_at", "updated_at"])


class Role(models.Model):
    name = models.CharField("角色名称", max_length=80)
    code = models.CharField("角色编码", max_length=64, choices=RoleCode.choices, unique=True)
    description = models.TextField("角色说明", blank=True)
    is_system = models.BooleanField("系统内置", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "角色"
        verbose_name_plural = "角色"
        ordering = ["code"]

    def __str__(self) -> str:
        return self.name


class UserRole(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_roles", verbose_name="用户")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_roles", verbose_name="角色")
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_user_roles",
        verbose_name="分配人",
        null=True,
        blank=True,
    )
    assigned_at = models.DateTimeField("分配时间", auto_now_add=True)

    class Meta:
        verbose_name = "用户角色"
        verbose_name_plural = "用户角色"
        unique_together = ("user", "role")

    def __str__(self) -> str:
        return f"{self.user} - {self.role}"
