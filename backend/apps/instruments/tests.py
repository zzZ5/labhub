import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.accounts.models import Role, RoleCode, UserRole

from .models import Instrument, InstrumentCategory

User = get_user_model()


@pytest.fixture
def member(db):
    user = User.objects.create_user(username="member", password="pass12345")
    user.profile.is_approved = True
    user.profile.save()
    role, _ = Role.objects.get_or_create(code=RoleCode.MEMBER, defaults={"name": "课题组成员"})
    UserRole.objects.get_or_create(user=user, role=role)
    return user


@pytest.fixture
def manager(db):
    user = User.objects.create_user(username="manager", password="pass12345")
    user.profile.is_approved = True
    user.profile.save()
    role, _ = Role.objects.get_or_create(code=RoleCode.INSTRUMENT_MANAGER, defaults={"name": "仪器管理员"})
    UserRole.objects.get_or_create(user=user, role=role)
    return user


@pytest.fixture
def instrument(db, manager):
    category = InstrumentCategory.objects.create(name="分析仪器", slug="analysis")
    return Instrument.objects.create(
        name="总有机碳分析仪",
        category=category,
        manager=manager,
        location_detail="B112",
        notes="使用前确认载气压力。",
    )


@pytest.mark.django_db
def test_instrument_list_requires_login(client):
    response = client.get(reverse("instrument-list"))

    assert response.status_code in {401, 403}


@pytest.mark.django_db
def test_member_can_view_instrument_details(client, member, instrument):
    client.login(username="member", password="pass12345")

    response = client.get(reverse("instrument-list"))

    assert response.status_code == 200
    assert response.json()[0]["name"] == "总有机碳分析仪"
    assert response.json()[0]["location_detail"] == "B112"
    assert response.json()[0]["notes"] == "使用前确认载气压力。"
    assert "need_training" not in response.json()[0]
    assert "serial_number" not in response.json()[0]


@pytest.mark.django_db
def test_member_cannot_edit_instrument(client, member, instrument):
    client.login(username="member", password="pass12345")

    response = client.patch(
        reverse("instrument-detail", args=[instrument.id]),
        {"name": "被越权修改的名称"},
        content_type="application/json",
    )

    assert response.status_code == 403
    instrument.refresh_from_db()
    assert instrument.name == "总有机碳分析仪"


@pytest.mark.django_db
def test_instrument_manager_can_update_core_fields(client, manager, instrument):
    client.login(username="manager", password="pass12345")

    response = client.patch(
        reverse("instrument-detail", args=[instrument.id]),
        {
            "location_detail": "环境分析实验室 B113",
            "status": Instrument.Status.MAINTENANCE,
            "notes": "维护期间暂停使用。",
        },
        content_type="application/json",
    )

    assert response.status_code == 200
    instrument.refresh_from_db()
    assert instrument.location_detail == "环境分析实验室 B113"
    assert instrument.status == Instrument.Status.MAINTENANCE


@pytest.mark.django_db
def test_removed_instrument_workflow_endpoints_return_not_found(client, manager):
    client.login(username="manager", password="pass12345")

    for path in ("training-records/", "maintenance-records/", "fault-reports/"):
        response = client.get(f"/api/instruments/{path}")
        assert response.status_code == 404
