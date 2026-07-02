from django.contrib import admin

from .models import Member, MemberEducation, MemberExperience


class MemberEducationInline(admin.TabularInline):
    model = MemberEducation
    extra = 0


class MemberExperienceInline(admin.TabularInline):
    model = MemberExperience
    extra = 0


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("name", "role_type", "research_direction", "sort_order")
    search_fields = ("name", "name_en", "research_direction", "email")
    inlines = [MemberEducationInline, MemberExperienceInline]
