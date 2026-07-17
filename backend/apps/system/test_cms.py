from io import BytesIO

import pytest
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from openpyxl import Workbook
from openpyxl.drawing.image import Image as WorksheetImage
from PIL import Image as PillowImage

from apps.accounts.models import Role, RoleCode, UserRole
from apps.instruments.models import Instrument
from apps.members.models import Member
from apps.portal.models import ResearchDirection
from apps.publications.models import Publication
from apps.system.cms_importers import import_members, import_publications, parse_publication_citation, read_rows_from_excel

User = get_user_model()


def test_parse_publication_citation_with_trailing_year():
    citation = (
        "Zhao, B., Shi, J., Zhao, R., Gao, S., Li, Y., Zhang, Y., Wei, Y., Guo, Y. "
        "Constructing CRISPR-Cas9 system for metabolic reprogramming and cordycepin "
        "biomanufacturing in Pichia pastoris, Bioresource Technology, 436, 132967. 2025"
    )

    parsed = parse_publication_citation(citation)

    assert parsed == {
        "authors": "Zhao, B., Shi, J., Zhao, R., Gao, S., Li, Y., Zhang, Y., Wei, Y., Guo, Y",
        "title": "Constructing CRISPR-Cas9 system for metabolic reprogramming and cordycepin biomanufacturing in Pichia pastoris",
        "journal": "Bioresource Technology",
        "year": "2025",
        "volume": "436",
        "issue": "",
        "pages": "132967",
        "doi": "",
    }


@pytest.mark.django_db
def test_member_import_keeps_image_rows_and_can_clear_avatar():
    keep = Member.objects.create(name="保留头像")
    keep.avatar.save("keep.gif", ContentFile(b"GIF89a"), save=True)
    clear = Member.objects.create(name="清空头像")
    clear.avatar.save("clear.gif", ContentFile(b"GIF89a"), save=True)

    result = import_members(
        [
            {"__row_number__": "2", "姓名": "保留头像", "头像": ""},
            {"__row_number__": "4", "姓名": "清空头像", "头像": "清空"},
        ],
        {},
    )

    keep.refresh_from_db()
    clear.refresh_from_db()
    assert keep.avatar
    assert not clear.avatar
    assert result["updated"] == 2


@pytest.mark.django_db
def test_member_excel_import_extracts_embedded_avatar():
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "导入数据"
    sheet.append(["姓名", "头像", "身份头衔", "研究方向", "排序"])
    sheet.append(["头像成员", "", "博士生", "堆肥微生物", 1])
    image_buffer = BytesIO()
    PillowImage.new("RGB", (10, 12), color=(0, 135, 60)).save(image_buffer, format="PNG")
    image_buffer.seek(0)
    sheet.add_image(WorksheetImage(PillowImage.open(image_buffer)), "B2")
    workbook_buffer = BytesIO()
    workbook.save(workbook_buffer)
    workbook_buffer.seek(0)

    rows, images = read_rows_from_excel(workbook_buffer)
    result = import_members(rows, {image.row_number: image for image in images})

    member = Member.objects.get(name="头像成员")
    assert result["created"] == 1
    assert result["images"] == 1
    assert member.avatar
    assert member.avatar.size > 0


@pytest.mark.django_db
def test_publication_import_updates_duplicate_doi():
    Publication.objects.create(
        title="旧题名",
        authors="旧作者",
        journal="旧期刊",
        year=2024,
        doi="10.1000/labhub",
    )

    result = import_publications([
        {
            "论文题目": "更新后的题名",
            "作者": "团队作者",
            "期刊": "Bioresource Technology",
            "年份": "2025",
            "DOI": "10.1000/LABHUB",
        },
    ])

    assert result == {"created": 0, "updated": 1, "skipped": 0, "images": 0, "total": 1}
    assert Publication.objects.count() == 1
    publication = Publication.objects.get()
    assert publication.title == "更新后的题名"
    assert publication.year == 2025


@pytest.mark.django_db(transaction=True)
def test_publication_import_rolls_back_all_rows_on_failure(monkeypatch):
    from apps.system import cms_importers

    original_upsert = cms_importers.upsert_record
    calls = 0

    def fail_on_second_row(model, lookup, defaults):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise ValueError("第二行模拟失败")
        return original_upsert(model, lookup, defaults)

    monkeypatch.setattr(cms_importers, "upsert_record", fail_on_second_row)

    with pytest.raises(ValueError, match="第二行模拟失败"):
        import_publications([
            {"论文题目": "第一篇", "年份": "2025"},
            {"论文题目": "第二篇", "年份": "2025"},
        ])

    assert not Publication.objects.exists()


@pytest.mark.django_db
def test_editor_can_parse_publication_citation(client):
    make_user("citation-editor", RoleCode.EDITOR)
    client.login(username="citation-editor", password="pass12345")
    citation = (
        "Zhao, B., Shi, J., Zhao, R., Gao, S., Li, Y., Zhang, Y., Wei, Y., Guo, Y. "
        "Constructing CRISPR-Cas9 system for metabolic reprogramming and cordycepin "
        "biomanufacturing in Pichia pastoris, Bioresource Technology, 436, 132967. 2025"
    )

    response = client.post(
        reverse("cms-publication-parse-citation"),
        {"citation": citation},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json()["complete"] is True
    assert response.json()["journal"] == "Bioresource Technology"
    assert response.json()["volume"] == "436"
    assert response.json()["pages"] == "132967"


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
    assert ResearchDirection.objects.filter(title="智能堆肥").exclude(slug="").exists()


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
    assert ResearchDirection.objects.get(title="封面方向").cover_image


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
            "location_detail": "A201",
            "status": Instrument.Status.NORMAL,
            "notes": "Use offline ledger for usage records.",
        },
        content_type="application/json",
    )

    assert response.status_code == 201
    assert Instrument.objects.filter(name="Compost reactor", location_detail="A201").exists()
