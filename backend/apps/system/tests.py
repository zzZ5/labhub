import pytest
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from rest_framework.serializers import ValidationError
from django.contrib.auth import get_user_model
from django.urls import reverse
from PIL import Image
from io import BytesIO

from apps.documents.models import Document, DocumentCategory, DocumentStatus
from apps.instruments.models import Instrument
from apps.students.models import StudentProfile
from apps.system.uploads import (
    AVATAR_UPLOAD_LIMIT,
    DOCUMENT_UPLOAD_LIMIT,
    IMAGE_UPLOAD_LIMIT,
    validate_avatar_upload,
    validate_document_upload,
    validate_image_upload,
)
from apps.system.image_compression import compress_field_file, profile_for_name


class SizedUpload:
    def __init__(self, size):
        self.size = size


@pytest.mark.parametrize(
    ("validator", "limit"),
    [
        (validate_avatar_upload, AVATAR_UPLOAD_LIMIT),
        (validate_image_upload, IMAGE_UPLOAD_LIMIT),
        (validate_document_upload, DOCUMENT_UPLOAD_LIMIT),
    ],
)
def test_upload_limits_are_specific_to_file_purpose(validator, limit):
    assert validator(SizedUpload(limit))
    with pytest.raises(ValidationError):
        validator(SizedUpload(limit + 1))


def test_image_compression_uses_smaller_avatar_profile(tmp_path):
    output = BytesIO()
    Image.new("RGB", (2400, 1800), "#6a8f72").save(output, format="JPEG", quality=96)
    storage = FileSystemStorage(location=tmp_path)
    name = storage.save("avatars/member.jpg", ContentFile(output.getvalue()))
    field_file = type("StoredImage", (), {"storage": storage, "name": name})()

    result = compress_field_file(field_file)

    assert profile_for_name(name).max_edge == 640
    assert result is not None
    assert field_file.name.endswith(".webp")
    assert result["width"] <= 640
    assert result["height"] <= 640
    assert result["size"] < result["original_size"]
    assert not storage.exists(name)
    assert storage.exists(field_file.name)


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
    StudentProfile.objects.create(user=user, name="测试学生", degree_type=StudentProfile.DegreeType.MASTER)

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
    assert payload["summary"][1] == {"label": "设备数量", "value": 1, "note": "仪器平台全部设备"}
    assert payload["summary"][2] == {"label": "资料数量", "value": 1, "note": "当前权限范围内"}
    assert payload["summary"][3] == {"label": "学生档案数量", "value": 1, "note": "当前可见学生档案"}
    assert payload["instrument_status"][0]["name"] == "总有机碳分析仪"
    assert payload["latest_documents"][0]["title"] == "堆肥反应器操作 SOP"
