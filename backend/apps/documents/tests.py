from io import BytesIO
from pathlib import Path
from unittest.mock import Mock
from zipfile import ZipFile

import pytest
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.urls import reverse
from openpyxl import Workbook

from apps.accounts.models import Role, RoleCode, UserRole

from .models import Document, DocumentCategory, DocumentDownloadLog, DocumentStatus
from .views import convert_embedded_image_to_png

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


def build_import_workbook_bytes():
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "导入数据"
    sheet.append(["资料标题", "资料分类", "资料说明", "文件名", "允许下载"])
    sheet.append(["批量导入实验方法", "实验方法", "批量导入测试。", "", "是"])
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def make_approved_user(username, role_code=RoleCode.MEMBER):
    user = User.objects.create_user(username=username, password="pass12345")
    user.profile.is_approved = True
    user.profile.save(update_fields=["is_approved"])
    role, _ = Role.objects.get_or_create(code=role_code, defaults={"name": role_code})
    UserRole.objects.get_or_create(user=user, role=role)
    return user


@pytest.fixture
def approved_user(db):
    return make_approved_user("member")


@pytest.fixture
def other_member(db):
    return make_approved_user("other-member")


@pytest.fixture
def document_manager(db):
    return make_approved_user("document-manager", RoleCode.DOCUMENT_MANAGER)


@pytest.fixture
def pending_user(db):
    return User.objects.create_user(username="pending", password="pass12345")


@pytest.fixture
def active_document(db, other_member):
    category = DocumentCategory.objects.create(name="实验方法", slug="methods")
    return Document.objects.create(
        title="堆肥反应器操作方法",
        category=category,
        status=DocumentStatus.ACTIVE,
        allow_download=True,
        owner=other_member,
        uploaded_by=other_member,
        file=ContentFile(b"hello labhub", name="method.txt"),
        original_filename="method.txt",
        file_size=11,
        file_type="text/plain",
    )


def test_convert_embedded_vector_image_to_png(monkeypatch):
    def fake_run(command, **kwargs):
        output_path = Path(command[-1]).with_suffix(".png")
        output_path.write_bytes(b"png-preview")
        return Mock(returncode=0)

    monkeypatch.setattr("apps.documents.views.shutil.which", lambda _name: "/usr/bin/libreoffice")
    monkeypatch.setattr("apps.documents.views.subprocess.run", fake_run)

    assert convert_embedded_image_to_png(b"vector-image", "word/media/diagram.emf") == b"png-preview"


@pytest.mark.django_db
def test_document_list_requires_approved_member(client, pending_user, active_document):
    anonymous = client.get(reverse("document-list"))
    client.force_login(pending_user)
    pending = client.get(reverse("document-list"))

    assert anonymous.status_code in {401, 403}
    assert pending.status_code == 403


@pytest.mark.django_db
def test_approved_member_can_view_all_active_documents(client, approved_user, active_document):
    Document.objects.create(title="另一份组内资料", status=DocumentStatus.ACTIVE)
    client.force_login(approved_user)

    response = client.get(reverse("document-list"))

    assert response.status_code == 200
    assert {item["title"] for item in response.json()} == {"堆肥反应器操作方法", "另一份组内资料"}


@pytest.mark.django_db
def test_document_download_and_preview_require_login(client, active_document):
    assert client.get(reverse("document-download", args=[active_document.id])).status_code == 401
    assert client.get(reverse("document-preview", args=[active_document.id])).status_code == 401


@pytest.mark.django_db
def test_pending_user_cannot_download(client, pending_user, active_document):
    client.force_login(pending_user)

    response = client.get(reverse("document-download", args=[active_document.id]))

    assert response.status_code == 403


@pytest.mark.django_db
def test_approved_member_can_download_and_log(client, approved_user, active_document):
    client.force_login(approved_user)

    response = client.get(reverse("document-download", args=[active_document.id]))

    assert response.status_code == 200
    assert response["Content-Disposition"].startswith("attachment;")
    assert DocumentDownloadLog.objects.filter(document=active_document, user=approved_user).exists()


@pytest.mark.django_db
def test_approved_member_can_preview_without_download_permission(client, approved_user):
    document = Document.objects.create(
        title="只允许在线查看的资料",
        status=DocumentStatus.ACTIVE,
        allow_download=False,
        file=ContentFile(b"preview", name="preview.txt"),
        original_filename="preview.txt",
        file_type="text/plain",
    )
    client.force_login(approved_user)

    response = client.get(reverse("document-preview", args=[document.id]))

    assert response.status_code == 200
    assert response["Content-Disposition"].startswith("inline;")
    assert response["X-Frame-Options"] == "SAMEORIGIN"


@pytest.mark.django_db
def test_docx_preview_is_rendered_as_embeddable_html(client, approved_user):
    document = Document.objects.create(
        title="Word 在线查看测试",
        status=DocumentStatus.ACTIVE,
        allow_download=False,
        file=ContentFile(build_docx_bytes("中农雨磷文档预览"), name="preview.docx"),
        original_filename="preview.docx",
        file_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    client.force_login(approved_user)

    response = client.get(reverse("document-preview", args=[document.id]))

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/html")
    assert "中农雨磷文档预览".encode() in response.content


@pytest.mark.django_db
def test_approved_member_can_upload_and_manage_own_document(client, approved_user):
    category = DocumentCategory.objects.create(name="实验方法", slug="upload-methods")
    client.force_login(approved_user)

    create_response = client.post(
        reverse("document-list"),
        {
            "title": "堆肥采样记录",
            "category_id": category.id,
            "status": DocumentStatus.ACTIVE,
            "allow_download": True,
            "file": ContentFile(b"template", name="template.txt"),
        },
    )

    assert create_response.status_code == 201
    document = Document.objects.get(title="堆肥采样记录")
    assert document.owner == approved_user
    assert document.uploaded_by == approved_user
    assert document.original_filename == "template.txt"
    assert document.file_size == 8

    update_response = client.patch(
        reverse("document-detail", args=[document.id]),
        {"title": "堆肥采样记录表"},
        content_type="application/json",
    )
    assert update_response.status_code == 200

    delete_response = client.delete(reverse("document-detail", args=[document.id]))
    assert delete_response.status_code == 204


@pytest.mark.django_db
def test_member_cannot_edit_or_delete_another_members_document(client, approved_user, active_document):
    client.force_login(approved_user)

    update_response = client.patch(
        reverse("document-detail", args=[active_document.id]),
        {"title": "越权修改"},
        content_type="application/json",
    )
    delete_response = client.delete(reverse("document-detail", args=[active_document.id]))

    assert update_response.status_code == 403
    assert delete_response.status_code == 403
    assert Document.objects.filter(pk=active_document.id).exists()


@pytest.mark.django_db
def test_document_manager_can_edit_and_delete_another_members_document(client, document_manager, active_document):
    client.force_login(document_manager)

    update_response = client.patch(
        reverse("document-detail", args=[active_document.id]),
        {"description": "管理员补充说明"},
        content_type="application/json",
    )
    delete_response = client.delete(reverse("document-detail", args=[active_document.id]))

    assert update_response.status_code == 200
    assert delete_response.status_code == 204


@pytest.mark.django_db
def test_approved_member_can_import_documents_with_simplified_template(client, approved_user):
    DocumentCategory.objects.create(name="实验方法", slug="import-methods")
    client.force_login(approved_user)

    response = client.post(
        reverse("document-import-excel"),
        {"file": ContentFile(build_import_workbook_bytes(), name="documents.xlsx")},
    )

    assert response.status_code == 200
    assert response.json()["created"] == 1
    document = Document.objects.get(title="批量导入实验方法")
    assert document.owner == approved_user
    assert document.description == "批量导入测试。"
