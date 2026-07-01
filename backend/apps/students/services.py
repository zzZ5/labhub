from django.db.models import Q

from apps.accounts.models import RoleCode
from apps.accounts.services import is_approved_member, user_has_role

from .models import StudentProfile, StudentVisibility


def is_student_owner(user, student: StudentProfile) -> bool:
    return bool(user and user.is_authenticated and student.user_id == user.id)


def can_manage_student_archives(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or user_has_role(user, RoleCode.ADMIN, RoleCode.PI)


def is_student_supervisor(user, student: StudentProfile) -> bool:
    if not user or not user.is_authenticated:
        return False
    if student.supervisor_id == user.id:
        return True
    return student.advisors.filter(id=user.id).exists()


def can_view_student_profile(user, student: StudentProfile) -> bool:
    if is_student_owner(user, student):
        return True
    if not is_approved_member(user):
        return False
    if can_manage_student_archives(user) or is_student_supervisor(user, student):
        return True
    return student.visibility == StudentVisibility.MEMBERS


def can_edit_student_profile(user, student: StudentProfile) -> bool:
    return is_student_owner(user, student) or can_manage_student_archives(user) or is_student_supervisor(user, student)


def can_delete_student_profile(user, student: StudentProfile) -> bool:
    return is_student_owner(user, student) or bool(user and user.is_authenticated and (user.is_superuser or user_has_role(user, RoleCode.ADMIN)))


def can_view_archive_file(user, archive_file) -> bool:
    student = archive_file.student
    if is_student_owner(user, student):
        return True
    if archive_file.visibility == StudentVisibility.PRIVATE:
        return False
    if archive_file.visibility == StudentVisibility.MEMBERS:
        return is_approved_member(user)
    if archive_file.visibility == StudentVisibility.SUPERVISOR:
        return is_student_supervisor(user, student) or can_manage_student_archives(user)
    if archive_file.visibility == StudentVisibility.PI:
        return can_manage_student_archives(user)
    return False


def can_delete_archive_file(user, archive_file) -> bool:
    return can_delete_student_profile(user, archive_file.student)


def visible_students_for_user(user, queryset):
    if not is_approved_member(user):
        return queryset.filter(user=user) if user and user.is_authenticated else queryset.none()
    if can_manage_student_archives(user):
        return queryset
    return queryset.filter(Q(user=user) | Q(supervisor=user) | Q(advisors=user) | Q(visibility=StudentVisibility.MEMBERS))
