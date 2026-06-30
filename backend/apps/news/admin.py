from django.contrib import admin

from .models import NewsArticle, NewsCategory, NewsImage, NewsTag


class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 0


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(NewsTag)
class NewsTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "visibility", "status", "is_pinned", "event_date", "updated_at")
    list_filter = ("visibility", "status", "is_pinned", "category")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "summary", "content")
    filter_horizontal = ("tags",)
    inlines = [NewsImageInline]
