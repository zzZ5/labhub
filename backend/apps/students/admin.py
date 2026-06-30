from django.contrib import admin

from .models import StudentArchiveFile, StudentProfile


class StudentArchiveFileInline(admin.TabularInline):
    model = StudentArchiveFile
    extra = 0
    readonly_fields = ("uploaded_at", "original_filename")


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "degree_type", "grade", "supervisor", "research_topic", "visibility", "updated_at")
    list_filter = ("degree_type", "grade", "visibility")
    search_fields = ("name", "research_topic", "research_direction", "user__username")
    inlines = [StudentArchiveFileInline]


admin.site.register(StudentArchiveFile)
