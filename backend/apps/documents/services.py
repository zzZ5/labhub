from apps.accounts.models import RoleCode
from apps.accounts.services import can_write_internal_data, is_approved_member, user_has_role

from .models import Document


def can_view_document(user, document: Document) -> bool:
    return is_approved_member(user)


def can_download_document(user, document: Document) -> bool:
    if not document.allow_download:
        return False
    return can_view_document(user, document)


def can_manage_documents(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return can_write_internal_data(user) and user_has_role(user, RoleCode.ADMIN, RoleCode.DOCUMENT_MANAGER)


def can_upload_document(user) -> bool:
    return is_approved_member(user)


def can_edit_document(user, document: Document) -> bool:
    if can_manage_documents(user):
        return True
    return bool(user and user.is_authenticated and document.owner_id == user.id)


def can_delete_document(user, document: Document) -> bool:
    return can_edit_document(user, document)


def visible_documents_for_user(user, queryset):
    return queryset if is_approved_member(user) else queryset.none()
