from apps.accounts.models import RoleCode
from apps.accounts.services import can_write_internal_data, is_approved_member, user_has_role

from .models import StudentProfile


def is_student_owner(user, student: StudentProfile) -> bool:
    return bool(user and user.is_authenticated and student.user_id == user.id)


def can_manage_student_archives(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    return can_write_internal_data(user) and (user.is_superuser or user_has_role(user, RoleCode.ADMIN))


def is_student_supervisor(user, student: StudentProfile) -> bool:
    if not user or not user.is_authenticated:
        return False
    if student.supervisor_id == user.id:
        return True
    return student.advisors.filter(id=user.id).exists()


def can_view_student_profile(user, student: StudentProfile) -> bool:
    return is_approved_member(user)


def can_edit_student_profile(user, student: StudentProfile) -> bool:
    return can_write_internal_data(user) and (
        is_student_owner(user, student) or can_manage_student_archives(user)
    )


def can_delete_student_profile(user, student: StudentProfile) -> bool:
    return can_write_internal_data(user) and (
        is_student_owner(user, student) or bool(user and (user.is_superuser or user_has_role(user, RoleCode.ADMIN)))
    )


def can_view_archive_file(user, archive_file) -> bool:
    return is_approved_member(user)


def can_delete_archive_file(user, archive_file) -> bool:
    return can_delete_student_profile(user, archive_file.student)


def can_edit_archive_file(user, archive_file) -> bool:
    return can_edit_student_profile(user, archive_file.student)


def visible_students_for_user(user, queryset):
    return queryset if is_approved_member(user) else queryset.none()
