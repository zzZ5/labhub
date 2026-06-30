from django.conf import settings
from django.db import models

from apps.documents.storage import ProtectedMediaStorage


protected_storage = ProtectedMediaStorage()


class StudentVisibility(models.TextChoices):
    PRIVATE = "private", "本人可见"
    SUPERVISOR = "supervisor", "本人/导师可见"
    PI = "pi", "硕博导师/管理员可见"
    MEMBERS = "members", "成员可见"


class StudentProfile(models.Model):
    class DegreeType(models.TextChoices):
        MASTER = "master", "硕士"
        PHD = "phd", "博士"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile", verbose_name="用户")
    name = models.CharField("姓名", max_length=80)
    degree_type = models.CharField("学位类型", max_length=20, choices=DegreeType.choices)
    grade = models.CharField("年级", max_length=40, blank=True)
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="supervised_students", verbose_name="导师", null=True, blank=True)
    research_topic = models.CharField("研究题目", max_length=240, blank=True)
    research_direction = models.CharField("研究方向", max_length=200, blank=True)
    enrollment_date = models.DateField("入学日期", null=True, blank=True)
    graduation_date = models.DateField("毕业日期", null=True, blank=True)
    destination = models.CharField("毕业去向", max_length=200, blank=True)
    visibility = models.CharField("可见性", max_length=20, choices=StudentVisibility.choices, default=StudentVisibility.SUPERVISOR)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "学生档案"
        verbose_name_plural = "学生档案"
        ordering = ["-grade", "name"]

    def __str__(self) -> str:
        return self.name


class StudentArchiveFile(models.Model):
    class FileType(models.TextChoices):
        PROPOSAL_REPORT = "proposal_report", "开题报告"
        PROPOSAL_PPT = "proposal_ppt", "开题 PPT"
        MIDTERM_REPORT = "midterm_report", "中期报告"
        MIDTERM_PPT = "midterm_ppt", "中期 PPT"
        PRE_DEFENSE_PPT = "pre_defense_ppt", "预答辩 PPT"
        THESIS = "thesis", "毕业论文"
        DEFENSE_PPT = "defense_ppt", "答辩 PPT"
        RAW_DATA_NOTE = "raw_data_note", "原始数据说明"
        CODE = "code", "代码"
        PAPER = "paper", "发表论文"
        HANDOVER = "handover", "毕业交接材料"

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="archive_files", verbose_name="学生")
    file_type = models.CharField("文件类型", max_length=40, choices=FileType.choices)
    title = models.CharField("标题", max_length=200)
    file = models.FileField("文件", storage=protected_storage, upload_to="students/archive/")
    preview_pdf = models.FileField("PDF 预览文件", storage=protected_storage, upload_to="students/archive/previews/", blank=True)
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
    version = models.CharField("版本", max_length=40, default="v1.0")
    visibility = models.CharField("可见性", max_length=20, choices=StudentVisibility.choices, default=StudentVisibility.SUPERVISOR)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="uploaded_student_files", verbose_name="上传人", null=True, blank=True)
    uploaded_at = models.DateTimeField("上传时间", auto_now_add=True)
    description = models.TextField("说明", blank=True)

    class Meta:
        verbose_name = "学生归档文件"
        verbose_name_plural = "学生归档文件"
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if self.file and not self.original_filename:
            self.original_filename = self.file.name.split("/")[-1]
        super().save(*args, **kwargs)
