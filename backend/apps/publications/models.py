from decimal import Decimal

from django.db import models

from apps.news.models import Visibility


class Publication(models.Model):
    title = models.CharField("论文题目", max_length=300)
    authors = models.TextField("作者")
    journal = models.CharField("期刊", max_length=200, blank=True)
    year = models.PositiveIntegerField("年份", db_index=True)
    volume = models.CharField("卷", max_length=50, blank=True)
    issue = models.CharField("期", max_length=50, blank=True)
    pages = models.CharField("页码", max_length=80, blank=True)
    doi = models.CharField("DOI", max_length=160, blank=True)
    impact_factor = models.DecimalField("影响因子", max_digits=6, decimal_places=2, null=True, blank=True)
    jcr_partition = models.CharField("JCR 分区", max_length=40, blank=True)
    cas_partition = models.CharField("中科院分区", max_length=40, blank=True)
    abstract = models.TextField("摘要", blank=True)
    pdf_file = models.FileField("PDF 文件", upload_to="publications/papers/", blank=True)
    visibility = models.CharField("可见性", max_length=20, choices=Visibility.choices, default=Visibility.PUBLIC)
    is_representative = models.BooleanField("代表性成果", default=False)
    sort_order = models.PositiveIntegerField("排序", default=0)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "论文"
        verbose_name_plural = "论文"
        ordering = ["-year", "sort_order", "-created_at"]

    def __str__(self) -> str:
        return self.title


class Project(models.Model):
    title = models.CharField("项目名称", max_length=240)
    project_number = models.CharField("项目编号", max_length=100, blank=True)
    funding_source = models.CharField("资助来源", max_length=160, blank=True)
    principal_investigator = models.CharField("负责人", max_length=80, blank=True)
    start_date = models.DateField("开始日期", null=True, blank=True)
    end_date = models.DateField("结束日期", null=True, blank=True)
    amount = models.DecimalField("经费", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField("状态", max_length=80, blank=True)
    visibility = models.CharField("可见性", max_length=20, choices=Visibility.choices, default=Visibility.PUBLIC)
    description = models.TextField("说明", blank=True)

    class Meta:
        verbose_name = "项目"
        verbose_name_plural = "项目"
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return self.title


class Patent(models.Model):
    title = models.CharField("专利名称", max_length=240)
    patent_number = models.CharField("专利号", max_length=120, blank=True)
    inventors = models.TextField("发明人", blank=True)
    application_date = models.DateField("申请日期", null=True, blank=True)
    authorization_date = models.DateField("授权日期", null=True, blank=True)
    status = models.CharField("状态", max_length=80, blank=True)
    visibility = models.CharField("可见性", max_length=20, choices=Visibility.choices, default=Visibility.PUBLIC)

    class Meta:
        verbose_name = "专利"
        verbose_name_plural = "专利"
        ordering = ["-application_date"]

    def __str__(self) -> str:
        return self.title


class SoftwareCopyright(models.Model):
    title = models.CharField("软著名称", max_length=240)
    registration_number = models.CharField("登记号", max_length=120, blank=True)
    authors = models.TextField("作者", blank=True)
    registration_date = models.DateField("登记日期", null=True, blank=True)
    visibility = models.CharField("可见性", max_length=20, choices=Visibility.choices, default=Visibility.PUBLIC)

    class Meta:
        verbose_name = "软件著作权"
        verbose_name_plural = "软件著作权"

    def __str__(self) -> str:
        return self.title


class Award(models.Model):
    title = models.CharField("奖励名称", max_length=240)
    award_level = models.CharField("奖励等级", max_length=120, blank=True)
    award_date = models.DateField("获奖日期", null=True, blank=True)
    participants = models.TextField("参与人员", blank=True)
    description = models.TextField("说明", blank=True)
    visibility = models.CharField("可见性", max_length=20, choices=Visibility.choices, default=Visibility.PUBLIC)

    class Meta:
        verbose_name = "奖励"
        verbose_name_plural = "奖励"
        ordering = ["-award_date"]

    def __str__(self) -> str:
        return self.title


class Standard(models.Model):
    title = models.CharField("标准名称", max_length=240)
    standard_number = models.CharField("标准号", max_length=120, blank=True)
    publish_date = models.DateField("发布日期", null=True, blank=True)
    participants = models.TextField("参与人员", blank=True)
    visibility = models.CharField("可见性", max_length=20, choices=Visibility.choices, default=Visibility.PUBLIC)

    class Meta:
        verbose_name = "标准"
        verbose_name_plural = "标准"
        ordering = ["-publish_date"]

    def __str__(self) -> str:
        return self.title


class Book(models.Model):
    title = models.CharField("著作名称", max_length=240)
    authors = models.TextField("作者", blank=True)
    publisher = models.CharField("出版社", max_length=160, blank=True)
    publish_date = models.DateField("出版日期", null=True, blank=True)
    isbn = models.CharField("ISBN", max_length=80, blank=True)
    visibility = models.CharField("可见性", max_length=20, choices=Visibility.choices, default=Visibility.PUBLIC)

    class Meta:
        verbose_name = "著作"
        verbose_name_plural = "著作"
        ordering = ["-publish_date"]

    def __str__(self) -> str:
        return self.title
