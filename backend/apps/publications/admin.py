from django.contrib import admin

from .models import Award, Book, Patent, Project, Publication, SoftwareCopyright, Standard


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ("title", "journal", "year", "visibility", "is_representative", "sort_order")
    list_filter = ("year", "visibility", "is_representative")
    search_fields = ("title", "authors", "journal", "doi")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "funding_source", "principal_investigator", "status", "visibility")
    list_filter = ("status", "visibility", "funding_source")
    search_fields = ("title", "project_number", "principal_investigator")


@admin.register(Patent)
class PatentAdmin(admin.ModelAdmin):
    list_display = ("title", "patent_number", "status", "application_date", "visibility")
    list_filter = ("status", "visibility")
    search_fields = ("title", "patent_number", "inventors")


admin.site.register(SoftwareCopyright)
admin.site.register(Award)
admin.site.register(Standard)
admin.site.register(Book)
