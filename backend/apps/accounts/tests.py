import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import Role, RoleCode, UserRole
from .services import can_manage_accounts, is_approved_member, user_has_role

User = get_user_model()


@pytest.fixture
def admin_user(db):
    user = User.objects.create_superuser(username="admin", email="admin@example.com", password="pass12345")
    user.profile.is_approved = True
    user.profile.role_type = "admin"
    user.profile.save()
    role, _ = Role.objects.get_or_create(name="系统管理员", code=RoleCode.ADMIN)
    UserRole.objects.create(user=user, role=role)
    return user


@pytest.fixture
def member_role(db):
    role, _ = Role.objects.get_or_create(name="课题组成员", code=RoleCode.MEMBER)
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
def test_pending_user_cannot_manage_accounts(client):
    User.objects.create_user(username="pending", password="pass12345")
    client.login(username="pending", password="pass12345")

    response = client.get(reverse("account-user-list"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_can_approve_user_and_assign_role(client, admin_user, member_role):
    target = User.objects.create_user(username="target", password="pass12345")
    client.login(username="admin", password="pass12345")

    approve_response = client.post(
        reverse("account-user-approve", args=[target.id]),
        {"is_approved": True, "role_type": "member"},
        content_type="application/json",
    )
    role_response = client.post(
        reverse("account-user-assign-role", args=[target.id]),
        {"role_code": RoleCode.MEMBER},
        content_type="application/json",
    )

    target.refresh_from_db()
    assert approve_response.status_code == 200
    assert role_response.status_code == 200
    assert target.profile.is_approved is True
    assert user_has_role(target, RoleCode.MEMBER)


@pytest.mark.django_db
def test_permission_helpers(admin_user):
    assert is_approved_member(admin_user)
    assert can_manage_accounts(admin_user)
    assert user_has_role(admin_user, RoleCode.ADMIN)
