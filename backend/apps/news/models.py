from django.conf import settings
from django.db import models


class Visibility(models.TextChoices):
    PUBLIC = "public", "公开"
    MEMBERS = "members", "成员可见"
    ADMINS = "admins", "管理员可见"


class NewsCategory(models.Model):
    name = models.CharField("分类名称", max_length=80)
    slug = models.SlugField("URL 标识", max_length=120, unique=True)
    description = models.TextField("说明", blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0)

    class Meta:
        verbose_name = "新闻分类"
        verbose_name_plural = "新闻分类"
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


class NewsTag(models.Model):
    name = models.CharField("标签名称", max_length=60)
    slug = models.SlugField("URL 标识", max_length=100, unique=True)

    class Meta:
        verbose_name = "新闻标签"
        verbose_name_plural = "新闻标签"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class NewsArticle(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "草稿"
        PUBLISHED = "published", "已发布"
        ARCHIVED = "archived", "已归档"

    title = models.CharField("标题", max_length=200)
    slug = models.SlugField("URL 标识", max_length=220, unique=True)
    summary = models.TextField("摘要", blank=True)
    content = models.TextField("内容")
    cover_image = models.ImageField("封面图", upload_to="news/covers/", blank=True)
    word_file = models.FileField("Word 新闻稿", upload_to="news/word/", blank=True)
    category = models.ForeignKey(NewsCategory, on_delete=models.SET_NULL, related_name="articles", verbose_name="分类", null=True, blank=True)
    tags = models.ManyToManyField(NewsTag, related_name="articles", verbose_name="标签", blank=True)
    event_date = models.DateField("活动日期", null=True, blank=True)
    location = models.CharField("地点", max_length=200, blank=True)
    visibility = models.CharField("可见性", max_length=20, choices=Visibility.choices, default=Visibility.PUBLIC)
    is_pinned = models.BooleanField("置顶", default=False)
    status = models.CharField("状态", max_length=20, choices=Status.choices, default=Status.DRAFT)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="news_articles", verbose_name="作者", null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "新闻文章"
        verbose_name_plural = "新闻文章"
        ordering = ["-is_pinned", "-event_date", "-created_at"]

    def __str__(self) -> str:
        return self.title


class NewsImage(models.Model):
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name="images", verbose_name="文章")
    image = models.ImageField("图片", upload_to="news/images/")
    caption = models.CharField("图片说明", max_length=200, blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0)

    class Meta:
        verbose_name = "新闻图片"
        verbose_name_plural = "新闻图片"
        ordering = ["sort_order"]

    def __str__(self) -> str:
        return self.caption or self.article.title
