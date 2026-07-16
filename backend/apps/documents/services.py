from django.utils import timezone

from apps.accounts.models import RoleCode
from apps.accounts.services import can_write_internal_data, is_approved_member, user_has_min_role, user_has_role, user_role_codes

from .models import Document, DocumentPermission, DocumentVisibility


def _valid_permission_queryset(document: Document):
    now = timezone.now()
    return document.permissions.filter(can_view=True).filter(expires_at__isnull=True) | document.permissions.filter(
        can_view=True, expires_at__gt=now
    )


def has_custom_permission(user, document: Document, *, download: bool = False) -> bool:
    if not user or not user.is_authenticated:
        return False
    permissions = _valid_permission_queryset(document)
    if download:
        permissions = permissions.filter(can_download=True)
    roles = user_role_codes(user)
    return permissions.filter(user=user).exists() or permissions.filter(role__code__in=roles).exists()


def can_view_document(user, document: Document) -> bool:
    if document.visibility == DocumentVisibility.PUBLIC:
        return True
    if not is_approved_member(user):
        return False
    if user.is_superuser:
        return True
    if document.visibility == DocumentVisibility.MEMBERS:
        return True
    if document.visibility == DocumentVisibility.PHD:
        return user_has_min_role(user, RoleCode.PHD)
    if document.visibility == DocumentVisibility.PI:
        return user_has_min_role(user, RoleCode.PI)
    if document.visibility == DocumentVisibility.CUSTOM:
        return has_custom_permission(user, document)
    return False


def can_download_document(user, document: Document) -> bool:
    if not document.allow_download:
        return False
    if document.visibility == DocumentVisibility.CUSTOM:
        return has_custom_permission(user, document, download=True)
    return can_view_document(user, document)


def can_manage_documents(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return can_write_internal_data(user) and user_has_role(user, RoleCode.ADMIN, RoleCode.DOCUMENT_MANAGER)


def can_upload_document(user) -> bool:
    return can_manage_documents(user)


def can_edit_document(user, document: Document) -> bool:
    return can_manage_documents(user)


def can_delete_document(user, document: Document) -> bool:
    return can_edit_document(user, document)


def visible_documents_for_user(user, queryset):
    public = queryset.filter(visibility=DocumentVisibility.PUBLIC)
    if not is_approved_member(user):
        return public
    if user.is_superuser:
        return queryset
    visible_ids = [doc.id for doc in queryset if can_view_document(user, doc)]
    return queryset.filter(id__in=visible_ids)
