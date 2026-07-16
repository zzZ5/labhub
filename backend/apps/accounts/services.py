from django.contrib.auth.models import AnonymousUser

from .models import RoleCode, UserProfile


SYSTEM_PERMISSION_CODES = {
    RoleCode.INSTRUMENT_MANAGER,
    RoleCode.DOCUMENT_MANAGER,
    RoleCode.EDITOR,
    RoleCode.ADMIN,
}

SYSTEM_ROLES = [
    (RoleCode.INSTRUMENT_MANAGER, "仪器管理员", "维护仪器设备状态、图片、位置和使用说明。"),
    (RoleCode.DOCUMENT_MANAGER, "资料管理员", "上传、编辑和整理内部资料。"),
    (RoleCode.EDITOR, "网站编辑", "维护门户内容、新闻、成果和成员信息。"),
    (RoleCode.ADMIN, "系统管理员", "拥有全部系统权限。"),
]


def user_role_codes(user) -> set[str]:
    if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
        return set()
    if user.is_superuser:
        return {RoleCode.ADMIN}
    return set(user.user_roles.select_related("role").values_list("role__code", flat=True))


def user_has_role(user, *role_codes: str) -> bool:
    roles = user_role_codes(user)
    return bool(roles.intersection(role_codes))


def user_has_min_role(user, role_code: str) -> bool:
    if user_has_role(user, RoleCode.ADMIN):
        return True
    identity = user_school_identity(user)
    if role_code == RoleCode.PHD:
        return identity in {UserProfile.SchoolIdentity.PHD, UserProfile.SchoolIdentity.POSTDOC, UserProfile.SchoolIdentity.PI}
    if role_code == RoleCode.PI:
        return identity == UserProfile.SchoolIdentity.PI
    return user_has_role(user, role_code)


def user_school_identity(user) -> str:
    profile = getattr(user, "profile", None) if user and getattr(user, "is_authenticated", False) else None
    return getattr(profile, "school_identity", "")


def is_approved_member(user) -> bool:
    if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    profile = getattr(user, "profile", None)
    return bool(profile and profile.is_approved)


def can_write_internal_data(user) -> bool:
    return is_approved_member(user)


def can_manage_accounts(user) -> bool:
    return bool(can_write_internal_data(user) and (user.is_superuser or user_has_role(user, RoleCode.ADMIN)))


def can_manage_portal_content(user) -> bool:
    return bool(can_write_internal_data(user) and (user.is_superuser or user_has_role(user, RoleCode.ADMIN, RoleCode.EDITOR)))

