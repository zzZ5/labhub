from django.contrib import admin

from .models import WechatAccount, WechatArticle


@admin.register(WechatAccount)
class WechatAccountAdmin(admin.ModelAdmin):
    list_display = ("name", "source_type", "is_active", "last_sync_success_at", "updated_at")
    list_filter = ("source_type", "is_active")
    search_fields = ("name", "description", "source_url")


@admin.register(WechatArticle)
class WechatArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "account", "published_at", "is_visible", "is_manual")
    list_filter = ("account", "is_visible", "is_manual")
    search_fields = ("title", "summary", "source_url")
    date_hierarchy = "published_at"

