from django.contrib.auth.models import AnonymousUser

from .models import RoleCode

ROLE_HIERARCHY = {
    RoleCode.ADMIN: 100,
    RoleCode.PI: 90,
    RoleCode.EDITOR: 70,
    RoleCode.DOCUMENT_MANAGER: 70,
    RoleCode.INSTRUMENT_MANAGER: 70,
    RoleCode.PHD: 50,
    RoleCode.POSTDOC: 50,
    RoleCode.MASTER: 40,
    RoleCode.MEMBER: 30,
}

SYSTEM_ROLES = [
    (RoleCode.MEMBER, "课题组成员", "可访问普通内部资料、仪器平台和学生可见信息。"),
    (RoleCode.MASTER, "硕士生", "继承成员权限，可管理自己的学生信息与归档资料。"),
    (RoleCode.PHD, "博士生", "继承成员权限，可访问更高等级实验方法资料。"),
    (RoleCode.POSTDOC, "博士后", "课题组博士后身份，可访问成员内部资料和科研管理信息。"),
    (RoleCode.INSTRUMENT_MANAGER, "仪器管理员", "维护仪器设备状态、图片、位置和使用说明。"),
    (RoleCode.DOCUMENT_MANAGER, "资料管理员", "上传、编辑、归档资料与版本。"),
    (RoleCode.EDITOR, "网站编辑", "维护门户内容、新闻、成果和成员信息。"),
    (RoleCode.PI, "硕博导师", "查看学生完整档案和关键项目资料。"),
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
    roles = user_role_codes(user)
    required = ROLE_HIERARCHY.get(role_code, 999)
    return any(ROLE_HIERARCHY.get(role, 0) >= required for role in roles)


def is_approved_member(user) -> bool:
    if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    profile = getattr(user, "profile", None)
    return bool(profile and profile.is_approved)


def can_manage_accounts(user) -> bool:
    return bool(user and user.is_authenticated and (user.is_superuser or user_has_role(user, RoleCode.ADMIN, RoleCode.PI)))


def can_manage_portal_content(user) -> bool:
    return bool(user and user.is_authenticated and (user.is_superuser or user_has_role(user, RoleCode.ADMIN, RoleCode.PI, RoleCode.EDITOR)))
