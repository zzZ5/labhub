from django.contrib import admin

from .models import (
    Document,
    DocumentCategory,
    DocumentDownloadLog,
    DocumentTag,
)


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "slug", "sort_order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")


@admin.register(DocumentTag)
class DocumentTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "original_filename", "uploaded_by", "status", "allow_download", "updated_at")
    list_filter = ("status", "allow_download", "category")
    search_fields = ("title", "description")
    filter_horizontal = ("tags",)


@admin.register(DocumentDownloadLog)
class DocumentDownloadLogAdmin(admin.ModelAdmin):
    list_display = ("document", "user", "ip_address", "downloaded_at")
    list_filter = ("downloaded_at",)
    search_fields = ("document__title", "user__username", "ip_address")
    readonly_fields = ("document", "user", "ip_address", "user_agent", "downloaded_at")
