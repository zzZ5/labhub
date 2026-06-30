import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Role, RoleCode, UserRole

from .models import Instrument, InstrumentCategory, InstrumentTrainingRecord

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
    return Instrument.objects.create(name="总有机碳分析仪", category=category, manager=manager, need_training=True)


@pytest.mark.django_db
def test_instrument_list_requires_login(client):
    response = client.get(reverse("instrument-list"))

    assert response.status_code in {401, 403}


@pytest.mark.django_db
def test_member_can_view_instrument_status(client, member, instrument):
    client.login(username="member", password="pass12345")

    response = client.get(reverse("instrument-list"))

    assert response.status_code == 200
    assert response.json()[0]["name"] == "总有机碳分析仪"
    assert response.json()[0]["need_training"] is True
    assert response.json()[0]["training_passed"] is False


@pytest.mark.django_db
def test_training_record_marks_instrument_training_passed(client, member, instrument):
    InstrumentTrainingRecord.objects.create(instrument=instrument, user=member, training_date=timezone.localdate(), is_passed=True)
    client.login(username="member", password="pass12345")

    response = client.get(reverse("instrument-list"))

    assert response.status_code == 200
    assert response.json()[0]["training_passed"] is True


@pytest.mark.django_db
def test_manager_can_create_maintenance_record(client, manager, instrument):
    client.login(username="manager", password="pass12345")

    response = client.post(
        reverse("instrument-maintenance-record-list"),
        {
            "instrument": instrument.id,
            "maintenance_date": timezone.localdate().isoformat(),
            "maintenance_type": "例行维护",
            "description": "清洁管路并检查传感器。",
        },
        content_type="application/json",
    )

    assert response.status_code == 201
    assert response.json()["maintainer"] == manager.id
