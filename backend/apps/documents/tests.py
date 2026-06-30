import pytest
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.urls import reverse
from io import BytesIO
from zipfile import ZipFile

from apps.accounts.models import Role, RoleCode, UserRole

from .models import (
    Document,
    DocumentCategory,
    DocumentDownloadLog,
    DocumentPermission,
    DocumentStatus,
    DocumentVersion,
    DocumentVisibility,
)

User = get_user_model()


def build_docx_bytes(text):
    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr(
            "word/document.xml",
            f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:body>
</w:document>""",
        )
    return buffer.getvalue()


@pytest.fixture
def approved_user(db):
    user = User.objects.create_user(username="member", password="pass12345")
    user.profile.is_approved = True
    user.profile.save()
    role, _ = Role.objects.get_or_create(code=RoleCode.MEMBER, defaults={"name": "课题组成员"})
    UserRole.objects.get_or_create(user=user, role=role)
    return user


@pytest.fixture
def pending_user(db):
    return User.objects.create_user(username="pending", password="pass12345")


@pytest.fixture
def active_document(db):
    category = DocumentCategory.objects.create(name="实验 SOP", slug="sop")
    document = Document.objects.create(
        title="堆肥反应器 SOP",
        category=category,
        visibility=DocumentVisibility.MEMBERS,
        status=DocumentStatus.ACTIVE,
        allow_download=True,
    )
    DocumentVersion.objects.create(
        document=document,
        version="v1.0",
        file=ContentFile(b"hello labhub", name="sop.txt"),
        original_filename="sop.txt",
        is_current=True,
    )
    return document


@pytest.mark.django_db
def test_document_list_filters_by_visibility(client, approved_user):
    Document.objects.create(title="成员资料", visibility=DocumentVisibility.MEMBERS, status=DocumentStatus.ACTIVE)
    Document.objects.create(title="导师资料", visibility=DocumentVisibility.PI, status=DocumentStatus.ACTIVE)
    client.login(username="member", password="pass12345")

    response = client.get(reverse("document-list"))

    titles = [item["title"] for item in response.json()]
    assert "成员资料" in titles
    assert "导师资料" not in titles


@pytest.mark.django_db
def test_document_download_requires_login(client, active_document):
    response = client.get(reverse("document-download", args=[active_document.id]))

    assert response.status_code == 401


@pytest.mark.django_db
def test_document_preview_requires_login(client, active_document):
    response = client.get(reverse("document-preview", args=[active_document.id]))

    assert response.status_code == 401


@pytest.mark.django_db
def test_pending_user_cannot_download(client, pending_user, active_document):
    client.login(username="pending", password="pass12345")

    response = client.get(reverse("document-download", args=[active_document.id]))

    assert response.status_code == 403


@pytest.mark.django_db
def test_approved_member_can_download_and_log(client, approved_user, active_document):
    client.login(username="member", password="pass12345")

    response = client.get(reverse("document-download", args=[active_document.id]))

    assert response.status_code == 200
    assert response["Content-Disposition"].startswith("attachment;")
    assert DocumentDownloadLog.objects.filter(document=active_document, user=approved_user).exists()


@pytest.mark.django_db
def test_approved_member_can_preview_without_download_permission(client, approved_user):
    document = Document.objects.create(
        title="鍙湪绾挎煡鐪嬬殑璧勬枡",
        visibility=DocumentVisibility.MEMBERS,
        status=DocumentStatus.ACTIVE,
        allow_download=False,
    )
    DocumentVersion.objects.create(
        document=document,
        version="v1.0",
        file=ContentFile(b"preview", name="preview.txt"),
        original_filename="preview.txt",
        is_current=True,
    )
    client.login(username="member", password="pass12345")

    response = client.get(reverse("document-preview", args=[document.id]))

    assert response.status_code == 200
    assert response["Content-Disposition"].startswith("inline;")
    assert response["X-Frame-Options"] == "SAMEORIGIN"
    assert not DocumentDownloadLog.objects.filter(document=document, user=approved_user).exists()


@pytest.mark.django_db
def test_docx_preview_is_rendered_as_embeddable_html(client, approved_user):
    document = Document.objects.create(
        title="Word 在线查看测试",
        visibility=DocumentVisibility.MEMBERS,
        status=DocumentStatus.ACTIVE,
        allow_download=False,
    )
    DocumentVersion.objects.create(
        document=document,
        version="v1.0",
        file=ContentFile(build_docx_bytes("中农雨磷文档预览"), name="preview.docx"),
        original_filename="preview.docx",
        file_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        is_current=True,
    )
    client.login(username="member", password="pass12345")

    response = client.get(reverse("document-preview", args=[document.id]))

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/html")
    assert response["X-Frame-Options"] == "SAMEORIGIN"
    assert "中农雨磷文档预览".encode() in response.content


@pytest.mark.django_db
def test_custom_permission_allows_assigned_user(client, approved_user):
    document = Document.objects.create(title="指定资料", visibility=DocumentVisibility.CUSTOM, status=DocumentStatus.ACTIVE)
    DocumentVersion.objects.create(
        document=document,
        version="v1.0",
        file=ContentFile(b"custom", name="custom.txt"),
        original_filename="custom.txt",
        is_current=True,
    )
    DocumentPermission.objects.create(document=document, user=approved_user, can_view=True, can_download=True)
    client.login(username="member", password="pass12345")

    response = client.get(reverse("document-download", args=[document.id]))

    assert response.status_code == 200


@pytest.mark.django_db
def test_document_upload_requires_document_manager(client, approved_user):
    category = DocumentCategory.objects.create(name="实验 SOP", slug="upload-sop")
    client.login(username="member", password="pass12345")

    response = client.post(
        reverse("document-list"),
        {
            "title": "新资料",
            "category_id": category.id,
            "visibility": DocumentVisibility.MEMBERS,
            "status": DocumentStatus.ACTIVE,
            "version": "v1.0",
            "file": ContentFile(b"managed", name="managed.txt"),
        },
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_document_manager_can_upload_document_with_version(client):
    manager = User.objects.create_user(username="doc-manager", password="pass12345")
    manager.profile.is_approved = True
    manager.profile.save()
    role, _ = Role.objects.get_or_create(code=RoleCode.DOCUMENT_MANAGER, defaults={"name": "资料管理员"})
    UserRole.objects.create(user=manager, role=role)
    category = DocumentCategory.objects.create(name="实验 SOP", slug="managed-sop")
    client.login(username="doc-manager", password="pass12345")

    response = client.post(
        reverse("document-list"),
        {
            "title": "堆肥采样记录模板",
            "category_id": category.id,
            "visibility": DocumentVisibility.MEMBERS,
            "status": DocumentStatus.ACTIVE,
            "version": "v1.0",
            "change_log": "初始版本",
            "file": ContentFile(b"template", name="template.txt"),
        },
    )

    assert response.status_code == 201
    document = Document.objects.get(title="堆肥采样记录模板")
    assert document.versions.filter(version="v1.0", is_current=True).exists()
    assert document.maintainer == manager
