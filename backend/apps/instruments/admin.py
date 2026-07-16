from django.contrib import admin

from .models import Instrument, InstrumentCategory


@admin.register(InstrumentCategory)
class InstrumentCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ("name", "model", "category", "location_detail", "status", "manager")
    list_filter = ("status", "category")
    search_fields = ("name", "model", "location_detail", "notes")
