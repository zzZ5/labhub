from django.conf import settings
from django.db import models

class InstrumentCategory(models.Model):
    name = models.CharField("分类名称", max_length=100)
    slug = models.SlugField("URL 标识", max_length=120, unique=True)
    description = models.TextField("说明", blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0)

    class Meta:
        verbose_name = "仪器分类"
        verbose_name_plural = "仪器分类"
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


class Instrument(models.Model):
    class Status(models.TextChoices):
        NORMAL = "normal", "正常"
        MAINTENANCE = "maintenance", "维护中"
        DISABLED = "disabled", "停用"

    name = models.CharField("仪器名称", max_length=160)
    model = models.CharField("型号", max_length=120, blank=True)
    category = models.ForeignKey(InstrumentCategory, on_delete=models.SET_NULL, related_name="instruments", verbose_name="分类", null=True, blank=True)
    location_detail = models.CharField("详细位置", max_length=200, blank=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="managed_instruments", verbose_name="负责人", null=True, blank=True)
    image = models.ImageField("图片", upload_to="instruments/images/", blank=True)
    status = models.CharField("状态", max_length=20, choices=Status.choices, default=Status.NORMAL)
    notes = models.TextField("使用说明", blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "仪器"
        verbose_name_plural = "仪器"
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name
