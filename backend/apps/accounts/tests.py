import pytest
import base64
from io import BytesIO
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from django.urls import reverse
from openpyxl import Workbook

from apps.students.models import StudentProfile
from .models import Role, RoleCode, UserProfile, UserRole
from .services import can_manage_accounts, is_approved_member, user_has_role

User = get_user_model()


@pytest.fixture
def admin_user(db):
    user = User.objects.create_superuser(username="admin", email="admin@example.com", password="pass12345")
    user.profile.is_approved = True
    user.profile.school_identity = UserProfile.SchoolIdentity.PI
    user.profile.save()
    role, _ = Role.objects.get_or_create(name="系统管理员", code=RoleCode.ADMIN)
    UserRole.objects.create(user=user, role=role)
    return user


@pytest.fixture
def editor_role(db):
    role, _ = Role.objects.get_or_create(name="网站编辑", code=RoleCode.EDITOR)
    return role


@pytest.mark.django_db
def test_register_creates_pending_profile(client):
    response = client.post(
        reverse("auth-register"),
        {
            "username": "student",
            "email": "student@example.com",
            "password": "StrongPass123!",
            "real_name": "学生甲",
            "phone": "13800000000",
        },
        content_type="application/json",
    )

    assert response.status_code == 201
    user = User.objects.get(username="student")
    assert user.profile.real_name == "学生甲"
    assert user.profile.is_approved is False


@pytest.mark.django_db
def test_login_and_current_user(client):
    user = User.objects.create_user(username="member", password="pass12345")

    login_response = client.post(
        reverse("auth-login"),
        {"username": "member", "password": "pass12345"},
        content_type="application/json",
    )
    me_response = client.get(reverse("auth-me"))

    assert login_response.status_code == 200
    assert me_response.status_code == 200
    assert me_response.json()["username"] == user.username


@pytest.mark.django_db
def test_login_accepts_email_case_insensitively(client):
    user = User.objects.create_user(username="email-member", email="Member@Example.com", password="pass12345")

    response = client.post(
        reverse("auth-login"),
        {"username": "member@example.com", "password": "pass12345"},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json()["username"] == user.username


@pytest.mark.django_db
def test_disabled_account_cannot_login(client):
    User.objects.create_user(username="disabled-member", password="pass12345", is_active=False)

    response = client.post(
        reverse("auth-login"),
        {"username": "disabled-member", "password": "pass12345"},
        content_type="application/json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_member_can_update_own_profile_and_shared_avatar(client):
    user = User.objects.create_user(username="profile-member", password="pass12345")
    image_bytes = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    )
    avatar = SimpleUploadedFile("self-avatar.png", image_bytes, content_type="image/png")
    client.login(username="profile-member", password="pass12345")

    response = client.patch(
        reverse("auth-me"),
        data=encode_multipart(
            BOUNDARY,
            {"username": "profile-member-new", "real_name": "成员甲", "phone": "13800000000", "bio": "个人简介", "avatar": avatar},
        ),
        content_type=MULTIPART_CONTENT,
    )

    assert response.status_code == 200
    user.refresh_from_db()
    user.profile.refresh_from_db()
    assert user.username == "profile-member-new"
    assert user.profile.real_name == "成员甲"
    assert user.profile.phone == "13800000000"
    assert response.json()["profile"]["avatar"]
    assert client.get(reverse("auth-me")).json()["username"] == "profile-member-new"


@pytest.mark.django_db
def test_member_cannot_use_duplicate_username(client):
    User.objects.create_user(username="existing-name", password="pass12345")
    user = User.objects.create_user(username="profile-owner", password="pass12345")
    client.login(username="profile-owner", password="pass12345")

    response = client.patch(
        reverse("auth-me"),
        {"username": "Existing-Name"},
        content_type="application/json",
    )

    user.refresh_from_db()
    assert response.status_code == 400
    assert user.username == "profile-owner"


@pytest.mark.django_db
def test_member_can_change_password_and_keep_session(client):
    user = User.objects.create_user(username="password-member", password="pass12345")
    client.login(username="password-member", password="pass12345")

    response = client.post(
        reverse("auth-password"),
        {
            "current_password": "pass12345",
            "new_password": "NewStrongPass123!",
            "confirm_password": "NewStrongPass123!",
        },
        content_type="application/json",
    )
    me_response = client.get(reverse("auth-me"))

    user.refresh_from_db()
    assert response.status_code == 200
    assert user.check_password("NewStrongPass123!")
    assert me_response.status_code == 200


@pytest.mark.django_db
def test_password_change_rejects_wrong_current_password(client):
    User.objects.create_user(username="wrong-password", password="pass12345")
    client.login(username="wrong-password", password="pass12345")

    response = client.post(
        reverse("auth-password"),
        {
            "current_password": "wrong-value",
            "new_password": "NewStrongPass123!",
            "confirm_password": "NewStrongPass123!",
        },
        content_type="application/json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_pending_user_cannot_manage_accounts(client):
    User.objects.create_user(username="pending", password="pass12345")
    client.login(username="pending", password="pass12345")

    response = client.get(reverse("account-user-list"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_can_approve_user_and_assign_system_permission(client, admin_user, editor_role):
    target = User.objects.create_user(username="target", password="pass12345")
    client.login(username="admin", password="pass12345")

    approve_response = client.post(
        reverse("account-user-approve", args=[target.id]),
        {"is_approved": True, "school_identity": UserProfile.SchoolIdentity.MASTER},
        content_type="application/json",
    )
    role_response = client.post(
        reverse("account-user-assign-role", args=[target.id]),
        {"role_code": RoleCode.EDITOR},
        content_type="application/json",
    )

    target.refresh_from_db()
    assert approve_response.status_code == 200
    assert role_response.status_code == 200
    assert target.profile.is_approved is True
    assert target.profile.school_identity == UserProfile.SchoolIdentity.MASTER
    assert user_has_role(target, RoleCode.EDITOR)


@pytest.mark.django_db
def test_permission_helpers(admin_user):
    assert is_approved_member(admin_user)
    assert can_manage_accounts(admin_user)
    assert user_has_role(admin_user, RoleCode.ADMIN)


@pytest.mark.django_db
def test_supervisor_identity_does_not_grant_account_management(client):
    supervisor = User.objects.create_user(username="supervisor", password="pass12345")
    supervisor.profile.school_identity = UserProfile.SchoolIdentity.PI
    supervisor.profile.is_approved = True
    supervisor.profile.save()
    client.login(username="supervisor", password="pass12345")

    response = client.get(reverse("account-user-list"))

    assert response.status_code == 403
    assert can_manage_accounts(supervisor) is False


@pytest.mark.django_db
def test_former_member_keeps_login_until_explicitly_disabled(client):
    user = User.objects.create_user(username="graduate", password="pass12345")
    user.profile.school_identity = UserProfile.SchoolIdentity.MASTER
    user.profile.membership_status = UserProfile.MembershipStatus.FORMER
    user.profile.is_approved = True
    user.profile.save()

    response = client.post(
        reverse("auth-login"),
        {"username": "graduate", "password": "pass12345"},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json()["profile"]["membership_status"] == UserProfile.MembershipStatus.FORMER


@pytest.mark.django_db
def test_identity_role_cannot_be_assigned_as_system_permission(client, admin_user):
    target = User.objects.create_user(username="target-role", password="pass12345")
    client.login(username="admin", password="pass12345")

    response = client.post(
        reverse("account-user-assign-role", args=[target.id]),
        {"role_code": RoleCode.PHD},
        content_type="application/json",
    )

    assert response.status_code == 400


def account_import_file(rows):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "账号导入"
    sheet.append(["姓名", "邮箱", "账号名", "初始密码", "学校身份", "成员状态", "系统权限", "审核状态", "生成学生档案", "年级"])
    for row in rows:
        sheet.append(row)
    buffer = BytesIO()
    workbook.save(buffer)
    return ContentFile(buffer.getvalue(), name="accounts.xlsx")


@pytest.mark.django_db
def test_admin_can_import_accounts_and_create_student_profile(client, admin_user):
    client.force_login(admin_user)
    upload = account_import_file([
        ["测试学生", "student-import@example.com", "", "StrongImportPass123!", "博士生", "在组", "资料管理员", "是", "是", "2026级"],
        ["测试博士后", "", "postdoc-import", "StrongImportPass456!", "博士后", "在组", "", "是", "否", ""],
    ])

    response = client.post(reverse("account-user-import-excel"), {"file": upload})

    assert response.status_code == 200
    assert response.json()["created"] == 2
    assert response.json()["student_profiles"] == 1
    student = User.objects.get(email="student-import@example.com")
    assert student.username == "student-import@example.com"
    assert student.profile.school_identity == UserProfile.SchoolIdentity.PHD
    assert student.user_roles.filter(role__code=RoleCode.DOCUMENT_MANAGER).exists()
    assert StudentProfile.objects.get(user=student).grade == "2026级"
    postdoc = User.objects.get(username="postdoc-import")
    assert postdoc.email == ""
    assert postdoc.profile.school_identity == UserProfile.SchoolIdentity.POSTDOC


@pytest.mark.django_db
def test_admin_can_create_username_only_account(client, admin_user):
    client.force_login(admin_user)

    response = client.post(
        reverse("account-user-create-account"),
        {
            "real_name": "无邮箱成员",
            "username": "username-only-member",
            "email": "",
            "password": "StrongUsernamePass123!",
            "school_identity": UserProfile.SchoolIdentity.OTHER,
            "membership_status": UserProfile.MembershipStatus.ACTIVE,
            "is_approved": True,
            "system_roles": [],
        },
        content_type="application/json",
    )

    assert response.status_code == 201
    user = User.objects.get(username="username-only-member")
    assert user.email == ""
    assert user.check_password("StrongUsernamePass123!")


@pytest.mark.django_db
def test_account_import_skips_existing_account_without_changing_password(client, admin_user):
    existing = User.objects.create_user(username="existing-import", email="existing-import@example.com", password="OriginalPass123!")
    client.force_login(admin_user)
    upload = account_import_file([
        ["已有成员", "existing-import@example.com", "existing-import", "ReplacementPass123!", "硕士生", "在组", "", "是", "是", "2025级"],
    ])

    response = client.post(reverse("account-user-import-excel"), {"file": upload})

    existing.refresh_from_db()
    assert response.status_code == 200
    assert response.json()["created"] == 0
    assert response.json()["skipped"] == 1
    assert existing.check_password("OriginalPass123!")
    assert not StudentProfile.objects.filter(user=existing).exists()


@pytest.mark.django_db
def test_non_admin_cannot_import_accounts(client):
    member = User.objects.create_user(username="ordinary-member", password="pass12345")
    member.profile.is_approved = True
    member.profile.save(update_fields=["is_approved"])
    client.force_login(member)
    upload = account_import_file([
        ["无权限成员", "forbidden-import@example.com", "", "StrongImportPass123!", "硕士生", "在组", "", "是", "否", ""],
    ])

    response = client.post(reverse("account-user-import-excel"), {"file": upload})

    assert response.status_code == 403
    assert not User.objects.filter(email="forbidden-import@example.com").exists()
