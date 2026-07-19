from django.db import models


class Member(models.Model):
    name = models.CharField("姓名", max_length=80)
    name_en = models.CharField("英文名", max_length=120, blank=True)
    avatar = models.ImageField("头像", upload_to="members/avatars/", blank=True)
    role_type = models.CharField("身份头衔", max_length=120, blank=True, default="")
    grade = models.CharField("年级", max_length=40, blank=True)
    research_direction = models.CharField("研究方向", max_length=200, blank=True)
    email = models.EmailField("邮箱", blank=True)
    profile = models.TextField("个人简介", blank=True)
    join_date = models.DateField("加入日期", null=True, blank=True)
    graduation_date = models.DateField("毕业日期", null=True, blank=True)
    destination = models.CharField("毕业去向", max_length=200, blank=True)
    is_public = models.BooleanField("公开展示", default=True)
    sort_order = models.PositiveIntegerField("排序", default=0)
    view_count = models.PositiveIntegerField("浏览次数", default=0)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "成员"
        verbose_name_plural = "成员"
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


class MemberEducation(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="educations", verbose_name="成员")
    school = models.CharField("学校", max_length=160)
    degree = models.CharField("学位", max_length=80, blank=True)
    major = models.CharField("专业", max_length=120, blank=True)
    start_date = models.DateField("开始日期", null=True, blank=True)
    end_date = models.DateField("结束日期", null=True, blank=True)
    description = models.TextField("说明", blank=True)

    class Meta:
        verbose_name = "教育经历"
        verbose_name_plural = "教育经历"
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return f"{self.member} - {self.school}"


class MemberExperience(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="experiences", verbose_name="成员")
    organization = models.CharField("单位", max_length=160)
    position = models.CharField("职位", max_length=120, blank=True)
    start_date = models.DateField("开始日期", null=True, blank=True)
    end_date = models.DateField("结束日期", null=True, blank=True)
    description = models.TextField("说明", blank=True)

    class Meta:
        verbose_name = "工作/科研经历"
        verbose_name_plural = "工作/科研经历"
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return f"{self.member} - {self.organization}"
