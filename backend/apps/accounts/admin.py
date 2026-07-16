from django.contrib import admin

from .models import Role, UserProfile, UserRole


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "real_name", "school_identity", "membership_status", "is_approved", "updated_at")
    list_filter = ("school_identity", "membership_status", "is_approved")
    search_fields = ("user__username", "user__email", "real_name", "phone")
    readonly_fields = ("created_at", "updated_at", "approved_at")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_system", "created_at")
    list_filter = ("is_system",)
    search_fields = ("name", "code")


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "assigned_by", "assigned_at")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email", "role__name", "role__code")
