import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.documents.models import Document, DocumentCategory, DocumentStatus
from apps.instruments.models import Instrument


@pytest.mark.django_db
def test_health_check(client):
    response = client.get(reverse("health-check"))

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.django_db
def test_csrf_token_sets_cookie(client):
    response = client.get(reverse("csrf-token"))

    assert response.status_code == 200
    assert response.json()["csrfToken"]
    assert "csrftoken" in response.cookies


@pytest.mark.django_db
def test_dashboard_requires_authentication(client):
    response = client.get(reverse("dashboard-summary"))

    assert response.status_code in {401, 403}


@pytest.mark.django_db
def test_dashboard_summary_returns_workspace_snapshot(client):
    user = get_user_model().objects.create_user(username="member@example.com", password="pass12345")
    user.profile.is_approved = True
    user.profile.save(update_fields=["is_approved"])
    category, _ = DocumentCategory.objects.get_or_create(slug="sop", defaults={"name": "实验 SOP"})
    Document.objects.create(
        title="堆肥反应器操作 SOP",
        category=category,
        status=DocumentStatus.ACTIVE,
    )
    Instrument.objects.create(name="总有机碳分析仪", status=Instrument.Status.MAINTENANCE, location_detail="B112")

    client.force_login(user)
    response = client.get(reverse("dashboard-summary"))

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {
        "summary",
        "instrument_status",
        "latest_documents",
        "todos",
        "student_archives",
        "recent_downloads",
    }
    assert payload["summary"][1]["label"] == "设备需关注"
    assert payload["instrument_status"][0]["name"] == "总有机碳分析仪"
    assert payload["latest_documents"][0]["title"] == "堆肥反应器操作 SOP"
