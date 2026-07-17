import pytest
import base64
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from django.urls import reverse

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
