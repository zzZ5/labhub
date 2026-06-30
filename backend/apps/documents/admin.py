from django.contrib import admin

from .models import (
    Document,
    DocumentCategory,
    DocumentDownloadLog,
    DocumentFavorite,
    DocumentPermission,
    DocumentTag,
    DocumentVersion,
)


class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    extra = 0
    readonly_fields = ("uploaded_at", "file_size")


class DocumentPermissionInline(admin.TabularInline):
    model = DocumentPermission
    extra = 0


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "slug", "visibility", "sort_order")
    list_filter = ("visibility",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")


@admin.register(DocumentTag)
class DocumentTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "current_version", "visibility", "status", "allow_download", "updated_at")
    list_filter = ("visibility", "status", "allow_download", "category")
    search_fields = ("title", "description")
    filter_horizontal = ("tags",)
    inlines = [DocumentVersionInline, DocumentPermissionInline]


@admin.register(DocumentDownloadLog)
class DocumentDownloadLogAdmin(admin.ModelAdmin):
    list_display = ("document", "version", "user", "ip_address", "downloaded_at")
    list_filter = ("downloaded_at",)
    search_fields = ("document__title", "user__username", "ip_address")
    readonly_fields = ("document", "version", "user", "ip_address", "user_agent", "downloaded_at")


admin.site.register(DocumentFavorite)
