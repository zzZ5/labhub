from django.contrib import admin

from .models import ContactInfo, HomeBanner, ResearchDirection, SiteSetting


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("site_name", "contact_email", "contact_phone", "updated_at")


@admin.register(ResearchDirection)
class ResearchDirectionAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "sort_order", "is_active", "updated_at")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "summary", "content")


@admin.register(HomeBanner)
class HomeBannerAdmin(admin.ModelAdmin):
    list_display = ("title", "sort_order", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle")


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ("title", "email", "phone", "updated_at")
