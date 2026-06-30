from django.contrib import admin

from .models import (
    Instrument,
    InstrumentCategory,
    InstrumentFaultReport,
    InstrumentImage,
    InstrumentMaintenanceRecord,
    InstrumentQRCode,
    InstrumentTrainingRecord,
)


class InstrumentImageInline(admin.TabularInline):
    model = InstrumentImage
    extra = 0


@admin.register(InstrumentCategory)
class InstrumentCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ("name", "model", "category", "room", "status", "need_training", "manager")
    list_filter = ("status", "need_training", "category")
    search_fields = ("name", "model", "serial_number", "room")
    inlines = [InstrumentImageInline]


admin.site.register(InstrumentMaintenanceRecord)
admin.site.register(InstrumentFaultReport)
admin.site.register(InstrumentTrainingRecord)
admin.site.register(InstrumentQRCode)
