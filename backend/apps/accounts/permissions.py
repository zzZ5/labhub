from rest_framework.permissions import BasePermission

from .services import can_manage_accounts, can_manage_portal_content, is_approved_member


class IsApprovedMember(BasePermission):
    message = "账号尚未审核通过。"

    def has_permission(self, request, view):
        return is_approved_member(request.user)


class CanManageAccounts(BasePermission):
    message = "需要导师或系统管理员权限。"

    def has_permission(self, request, view):
        return can_manage_accounts(request.user)


class CanManagePortalContent(BasePermission):
    message = "需要网站编辑、导师或系统管理员权限。"

    def has_permission(self, request, view):
        return can_manage_portal_content(request.user)
