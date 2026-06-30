from django.conf import settings
from django.db import models

from apps.documents.models import Document


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
    serial_number = models.CharField("序列号", max_length=120, blank=True)
    category = models.ForeignKey(InstrumentCategory, on_delete=models.SET_NULL, related_name="instruments", verbose_name="分类", null=True, blank=True)
    room = models.CharField("房间", max_length=120, blank=True)
    location_detail = models.CharField("详细位置", max_length=200, blank=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="managed_instruments", verbose_name="管理员", null=True, blank=True)
    image = models.ImageField("图片", upload_to="instruments/images/", blank=True)
    status = models.CharField("状态", max_length=20, choices=Status.choices, default=Status.NORMAL)
    need_training = models.BooleanField("是否需要培训", default=False)
    sop_document = models.ForeignKey(Document, on_delete=models.SET_NULL, related_name="sop_instruments", verbose_name="SOP 文档", null=True, blank=True)
    notes = models.TextField("备注", blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "仪器"
        verbose_name_plural = "仪器"
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


class InstrumentImage(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name="images", verbose_name="仪器")
    image = models.ImageField("图片", upload_to="instruments/gallery/")
    caption = models.CharField("说明", max_length=200, blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0)

    class Meta:
        verbose_name = "仪器图片"
        verbose_name_plural = "仪器图片"
        ordering = ["sort_order"]

    def __str__(self) -> str:
        return self.caption or self.instrument.name


class InstrumentMaintenanceRecord(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name="maintenance_records", verbose_name="仪器")
    maintainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="instrument_maintenance_records", verbose_name="维护人", null=True, blank=True)
    maintenance_date = models.DateField("维护日期")
    maintenance_type = models.CharField("维护类型", max_length=120, blank=True)
    description = models.TextField("维护说明")
    cost = models.DecimalField("费用", max_digits=10, decimal_places=2, default=0)
    next_maintenance_date = models.DateField("下次维护日期", null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "仪器维护记录"
        verbose_name_plural = "仪器维护记录"

    def __str__(self) -> str:
        return f"{self.instrument} - {self.maintenance_date}"


class InstrumentFaultReport(models.Model):
    class Status(models.TextChoices):
        REPORTED = "reported", "已报修"
        PROCESSING = "processing", "处理中"
        RESOLVED = "resolved", "已解决"
        CLOSED = "closed", "已关闭"

    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name="fault_reports", verbose_name="仪器")
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="instrument_fault_reports", verbose_name="报告人", null=True, blank=True)
    fault_time = models.DateTimeField("故障时间")
    description = models.TextField("故障描述")
    status = models.CharField("状态", max_length=20, choices=Status.choices, default=Status.REPORTED)
    handled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="handled_instrument_faults", verbose_name="处理人", null=True, blank=True)
    handled_at = models.DateTimeField("处理时间", null=True, blank=True)
    result = models.TextField("处理结果", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "仪器故障报修"
        verbose_name_plural = "仪器故障报修"

    def __str__(self) -> str:
        return f"{self.instrument} - {self.get_status_display()}"


class InstrumentTrainingRecord(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name="training_records", verbose_name="仪器")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="instrument_training_records", verbose_name="受训人")
    trainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="given_instrument_trainings", verbose_name="培训人", null=True, blank=True)
    training_date = models.DateField("培训日期")
    is_passed = models.BooleanField("是否通过", default=False)
    certificate_file = models.FileField("培训证明", upload_to="instruments/training/", blank=True)
    notes = models.TextField("备注", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "仪器培训记录"
        verbose_name_plural = "仪器培训记录"
        unique_together = ("instrument", "user")

    def __str__(self) -> str:
        return f"{self.instrument} - {self.user}"


class InstrumentQRCode(models.Model):
    instrument = models.OneToOneField(Instrument, on_delete=models.CASCADE, related_name="qr_code", verbose_name="仪器")
    qr_code_image = models.ImageField("二维码图片", upload_to="instruments/qrcodes/", blank=True)
    url = models.URLField("入口 URL")
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "仪器二维码"
        verbose_name_plural = "仪器二维码"

    def __str__(self) -> str:
        return self.instrument.name
