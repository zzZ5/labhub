import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.accounts.models import Role, RoleCode, UserRole
from apps.instruments.models import Instrument
from apps.portal.models import ResearchDirection

User = get_user_model()


def make_user(username, role_code):
    user = User.objects.create_user(username=username, password="pass12345")
    user.profile.is_approved = True
    user.profile.save(update_fields=["is_approved"])
    role, _ = Role.objects.get_or_create(code=role_code, defaults={"name": role_code})
    UserRole.objects.create(user=user, role=role)
    return user


@pytest.mark.django_db
def test_member_cannot_manage_portal_content(client):
    make_user("member", RoleCode.MEMBER)
    client.login(username="member", password="pass12345")

    response = client.post(
        reverse("cms-research-direction-list"),
        {"title": "智能堆肥", "slug": "smart-compost", "summary": "过程建模与调控"},
        content_type="application/json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_editor_can_create_research_direction(client):
    make_user("editor", RoleCode.EDITOR)
    client.login(username="editor", password="pass12345")

    response = client.post(
        reverse("cms-research-direction-list"),
        {"title": "智能堆肥", "slug": "smart-compost", "summary": "过程建模与调控", "is_active": True},
        content_type="application/json",
    )

    assert response.status_code == 201
    assert ResearchDirection.objects.filter(slug="smart-compost").exists()


@pytest.mark.django_db
def test_editor_can_upload_research_cover(client):
    make_user("image-editor", RoleCode.EDITOR)
    client.login(username="image-editor", password="pass12345")
    image = SimpleUploadedFile(
        "cover.gif",
        b"GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
        content_type="image/gif",
    )

    response = client.post(
        reverse("cms-research-direction-list"),
        {
            "title": "封面方向",
            "slug": "cover-direction",
            "summary": "包含封面图",
            "cover_image": image,
            "is_active": "true",
        },
    )

    assert response.status_code == 201
    assert ResearchDirection.objects.get(slug="cover-direction").cover_image


@pytest.mark.django_db
def test_member_cannot_manage_instrument_content(client):
    make_user("instrument-member", RoleCode.MEMBER)
    client.login(username="instrument-member", password="pass12345")

    response = client.post(
        reverse("cms-instrument-list"),
        {"name": "Compost reactor", "status": Instrument.Status.NORMAL},
        content_type="application/json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_editor_can_create_instrument_content(client):
    make_user("instrument-editor", RoleCode.EDITOR)
    client.login(username="instrument-editor", password="pass12345")

    response = client.post(
        reverse("cms-instrument-list"),
        {
            "name": "Compost reactor",
            "model": "Pilot platform",
            "room": "A201",
            "status": Instrument.Status.NORMAL,
            "need_training": False,
            "notes": "Use offline ledger for usage records.",
        },
        content_type="application/json",
    )

    assert response.status_code == 201
    assert Instrument.objects.filter(name="Compost reactor", room="A201").exists()
