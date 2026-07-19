from django.db import models


class SiteSetting(models.Model):
    site_name = models.CharField("站点名称", max_length=120, blank=True, default="")
    site_subtitle = models.CharField("站点副标题", max_length=200, blank=True)
    logo = models.ImageField("Logo", upload_to="portal/logos/", blank=True)
    favicon = models.ImageField("Favicon", upload_to="portal/favicons/", blank=True)
    hero_image = models.ImageField("首页横幅图", upload_to="portal/hero/", blank=True)
    description = models.TextField("站点描述", blank=True)
    hero_subtitle = models.CharField("首页横幅副标题", max_length=300, blank=True)
    banner_interval_seconds = models.PositiveSmallIntegerField("横幅切换间隔（秒）", default=6)
    footer_text = models.TextField("页脚文字", blank=True)
    contact_email = models.EmailField("联系邮箱", blank=True)
    contact_phone = models.CharField("联系电话", max_length=50, blank=True)
    address = models.CharField("地址", max_length=300, blank=True)
    map_embed = models.TextField("地图嵌入代码", blank=True)
    external_links = models.JSONField("外部链接", default=list, blank=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "站点设置"
        verbose_name_plural = "站点设置"

    def __str__(self) -> str:
        return self.site_name


class ResearchDirection(models.Model):
    title = models.CharField("标题", max_length=160)
    slug = models.SlugField("URL 标识", max_length=180, unique=True)
    summary = models.TextField("摘要", blank=True)
    content = models.TextField("内容", blank=True)
    cover_image = models.ImageField("封面图", upload_to="portal/research/", blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0)
    is_active = models.BooleanField("是否启用", default=True)
    view_count = models.PositiveIntegerField("浏览次数", default=0)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "研究方向"
        verbose_name_plural = "研究方向"
        ordering = ["sort_order", "-created_at"]

    def __str__(self) -> str:
        return self.title


class HomeBanner(models.Model):
    title = models.CharField("标题", max_length=160)
    subtitle = models.CharField("副标题", max_length=260, blank=True)
    image = models.ImageField("图片", upload_to="portal/banners/", blank=True)
    link = models.URLField("链接", blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0)
    is_active = models.BooleanField("是否启用", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "首页轮播"
        verbose_name_plural = "首页轮播"
        ordering = ["sort_order", "-created_at"]

    def __str__(self) -> str:
        return self.title


class ContactInfo(models.Model):
    title = models.CharField("标题", max_length=120, default="联系我们")
    content = models.TextField("说明", blank=True)
    email = models.EmailField("邮箱", blank=True)
    phone = models.CharField("电话", max_length=50, blank=True)
    address = models.CharField("地址", max_length=300, blank=True)
    map_url = models.URLField("地图链接", blank=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "联系信息"
        verbose_name_plural = "联系信息"

    def __str__(self) -> str:
        return self.title
