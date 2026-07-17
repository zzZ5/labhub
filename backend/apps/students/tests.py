from django.core.files.base import ContentFile
import base64

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from django.urls import reverse

from apps.accounts.models import Role, RoleCode, UserProfile, UserRole

from .models import StudentArchiveFile, StudentProfile
from .services import can_view_student_profile

User = get_user_model()


@pytest.fixture
def student_user(db):
    user = User.objects.create_user(username="student", password="pass12345")
    user.profile.is_approved = True
    user.profile.school_identity = UserProfile.SchoolIdentity.MASTER
    user.profile.save()
    return user


@pytest.fixture
def pi_user(db):
    user = User.objects.create_user(username="pi", password="pass12345")
    user.profile.is_approved = True
    user.profile.school_identity = UserProfile.SchoolIdentity.PI
    user.profile.save()
    return user


@pytest.fixture
def admin_user(db):
    user = User.objects.create_user(username="archive-admin", password="pass12345")
    user.profile.is_approved = True
    user.profile.school_identity = UserProfile.SchoolIdentity.PI
    user.profile.save()
    role, _ = Role.objects.get_or_create(code=RoleCode.ADMIN, defaults={"name": "系统管理员"})
    UserRole.objects.get_or_create(user=user, role=role)
    return user


@pytest.fixture
def other_user(db):
    user = User.objects.create_user(username="other", password="pass12345")
    user.profile.is_approved = True
    user.profile.school_identity = UserProfile.SchoolIdentity.OTHER
    user.profile.save()
    return user


@pytest.fixture
def undergraduate_user(db):
    user = User.objects.create_user(username="undergraduate", password="pass12345")
    user.profile.is_approved = True
    user.profile.school_identity = UserProfile.SchoolIdentity.UNDERGRADUATE
    user.profile.save()
    return user


@pytest.fixture
def student_profile(student_user, pi_user):
    profile = StudentProfile.objects.create(
        user=student_user,
        name="李同学",
        degree_type=StudentProfile.DegreeType.MASTER,
        grade="2024级",
        supervisor=pi_user,
        research_topic="智能堆肥过程建模",
    )
    return profile


@pytest.mark.django_db
def test_student_can_view_own_profile(client, student_user, student_profile):
    client.login(username="student", password="pass12345")

    response = client.get(reverse("student-profile-me"))

    assert response.status_code == 200
    assert response.json()["name"] == "李同学"
    assert can_view_student_profile(student_user, student_profile)


@pytest.mark.django_db
def test_pi_can_view_supervised_students(client, pi_user, student_profile):
    client.login(username="pi", password="pass12345")

    response = client.get(reverse("student-profile-list"))

    assert response.status_code == 200
    assert response.json()[0]["name"] == "李同学"


@pytest.mark.django_db
def test_pi_account_cannot_be_bound_to_student_profile(client, pi_user):
    client.login(username="pi", password="pass12345")

    response = client.post(
        reverse("student-profile-list"),
        {
            "user": pi_user.id,
            "name": "导师账号",
            "degree_type": StudentProfile.DegreeType.MASTER,
            "grade": "2026级",
        },
    )

    assert response.status_code == 400
    assert not StudentProfile.objects.filter(user=pi_user).exists()


@pytest.mark.django_db
def test_undergraduate_account_can_be_bound_to_student_profile(client, admin_user, undergraduate_user):
    client.login(username="archive-admin", password="pass12345")

    response = client.post(
        reverse("student-profile-list"),
        {
            "user": undergraduate_user.id,
            "name": "本科同学",
            "degree_type": StudentProfile.DegreeType.UNDERGRADUATE,
            "grade": "2026级",
        },
    )

    assert response.status_code == 201
    assert StudentProfile.objects.filter(user=undergraduate_user, degree_type=StudentProfile.DegreeType.UNDERGRADUATE).exists()


@pytest.mark.django_db
def test_one_account_cannot_have_multiple_student_profiles(client, admin_user, student_user, student_profile):
    client.login(username="archive-admin", password="pass12345")

    response = client.post(
        reverse("student-profile-list"),
        {
            "user": student_user.id,
            "name": "重复档案",
            "degree_type": StudentProfile.DegreeType.MASTER,
        },
    )

    assert response.status_code == 400
    assert StudentProfile.objects.filter(user=student_user).count() == 1


@pytest.mark.django_db
def test_student_profile_supports_multiple_advisors(client, admin_user, pi_user, student_profile):
    second_advisor = User.objects.create_user(username="second-pi", email="second-pi@example.com", password="pass12345")
    second_advisor.profile.real_name = "第二导师"
    second_advisor.profile.school_identity = UserProfile.SchoolIdentity.PI
    second_advisor.profile.is_approved = True
    second_advisor.profile.save()
    client.login(username="archive-admin", password="pass12345")

    response = client.patch(
        reverse("student-profile-detail", args=[student_profile.id]),
        {"advisors": [pi_user.id, second_advisor.id]},
        content_type="application/json",
    )

    assert response.status_code == 200
    student_profile.refresh_from_db()
    assert set(student_profile.advisors.values_list("id", flat=True)) == {pi_user.id, second_advisor.id}
    assert set(response.json()["advisor_names"]) == {"pi", "第二导师"}


@pytest.mark.django_db
def test_student_without_system_permission_can_update_own_profile(client, student_user, student_profile):
    client.login(username="student", password="pass12345")

    detail_response = client.get(reverse("student-profile-detail", args=[student_profile.id]))
    update_response = client.patch(
        reverse("student-profile-detail", args=[student_profile.id]),
        {"research_topic": "学生本人修改"},
        content_type="application/json",
    )

    assert detail_response.status_code == 200
    assert update_response.status_code == 200
    student_profile.refresh_from_db()
    assert student_profile.research_topic == "学生本人修改"


@pytest.mark.django_db
def test_supervisor_can_view_but_cannot_update_student_profile(client, pi_user, student_profile):
    client.login(username="pi", password="pass12345")

    detail_response = client.get(reverse("student-profile-detail", args=[student_profile.id]))
    update_response = client.patch(
        reverse("student-profile-detail", args=[student_profile.id]),
        {"research_topic": "导师代改"},
        content_type="application/json",
    )

    assert detail_response.status_code == 200
    assert update_response.status_code == 403


@pytest.mark.django_db
def test_graduating_account_preserves_student_profile(client, admin_user, student_user, student_profile):
    client.login(username="archive-admin", password="pass12345")

    response = client.patch(
        reverse("account-user-update-account", args=[student_user.id]),
        {
            "membership_status": UserProfile.MembershipStatus.FORMER,
        },
        content_type="application/json",
    )

    assert response.status_code == 200
    student_user.profile.refresh_from_db()
    assert student_user.profile.membership_status == UserProfile.MembershipStatus.FORMER
    assert student_user.is_active is True
    assert StudentProfile.objects.filter(pk=student_profile.pk, user=student_user).exists()


@pytest.mark.django_db
def test_account_and_student_profile_share_one_avatar(client, admin_user, student_user, student_profile):
    image_bytes = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    )
    avatar = SimpleUploadedFile("student-avatar.png", image_bytes, content_type="image/png")
    client.login(username="archive-admin", password="pass12345")

    account_response = client.patch(
        reverse("account-user-update-account", args=[student_user.id]),
        data=encode_multipart(BOUNDARY, {"avatar": avatar}),
        content_type=MULTIPART_CONTENT,
    )
    student_response = client.get(reverse("student-profile-detail", args=[student_profile.id]))

    assert account_response.status_code == 200
    assert student_response.status_code == 200
    account_avatar = account_response.json()["profile"]["avatar"]
    assert account_avatar
    assert student_response.json()["avatar"] == account_avatar


@pytest.mark.django_db
def test_approved_member_can_view_all_student_profiles(client, other_user, student_profile):
    client.login(username="other", password="pass12345")

    response = client.get(reverse("student-profile-list"))

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [student_profile.id]


@pytest.mark.django_db
def test_approved_member_can_view_and_download_archive_file(client, other_user, student_profile):
    archive = StudentArchiveFile.objects.create(
        student=student_profile,
        file_type=StudentArchiveFile.FileType.PROPOSAL_REPORT,
        title="开题报告",
        file=ContentFile(b"proposal", name="proposal.txt"),
    )
    client.login(username="other", password="pass12345")

    detail_response = client.get(reverse("student-archive-file-detail", args=[archive.id]))
    preview_response = client.get(reverse("student-archive-file-preview", args=[archive.id]))
    download_response = client.get(reverse("student-archive-file-download", args=[archive.id]))

    assert detail_response.status_code == 200
    assert preview_response.status_code == 200
    assert download_response.status_code == 200


@pytest.mark.django_db
def test_student_can_upload_own_archive_file(client, student_user, student_profile):
    client.login(username="student", password="pass12345")

    response = client.post(
        reverse("student-archive-file-list"),
        {
            "student": student_profile.id,
            "file_type": StudentArchiveFile.FileType.PROPOSAL_REPORT,
            "title": "开题报告",
            "file": ContentFile(b"proposal", name="proposal.txt"),
        },
    )

    assert response.status_code == 201
    archive = StudentArchiveFile.objects.get(student=student_profile)
    assert archive.uploaded_by == student_user


@pytest.mark.django_db
def test_other_member_cannot_upload_archive_file(client, other_user, student_profile):
    client.login(username="other", password="pass12345")

    response = client.post(
        reverse("student-archive-file-list"),
        {
            "student": student_profile.id,
            "file_type": StudentArchiveFile.FileType.PROPOSAL_REPORT,
            "title": "开题报告",
            "file": ContentFile(b"proposal", name="proposal.txt"),
        },
    )

    assert response.status_code >= 400


@pytest.mark.django_db
def test_student_can_upload_own_thesis_file(client, student_user, student_profile):
    client.login(username="student", password="pass12345")

    response = client.post(
        reverse("student-archive-file-list"),
        {
            "student": student_profile.id,
            "file_type": StudentArchiveFile.FileType.THESIS,
            "title": "毕业论文",
            "file": ContentFile(b"thesis", name="thesis.pdf"),
        },
    )

    assert response.status_code == 201
    assert StudentArchiveFile.objects.filter(student=student_profile, file_type=StudentArchiveFile.FileType.THESIS).exists()


@pytest.mark.django_db
def test_supervisor_cannot_delete_student_profile(client, pi_user, student_profile):
    client.login(username="pi", password="pass12345")

    response = client.delete(reverse("student-profile-detail", args=[student_profile.id]))

    assert response.status_code == 403
    assert StudentProfile.objects.filter(pk=student_profile.pk).exists()


@pytest.mark.django_db
def test_student_can_delete_own_archive_file(client, student_user, student_profile):
    archive = StudentArchiveFile.objects.create(
        student=student_profile,
        file_type=StudentArchiveFile.FileType.PROPOSAL_REPORT,
        title="开题报告",
        file=ContentFile(b"proposal", name="proposal.txt"),
    )
    client.login(username="student", password="pass12345")

    response = client.delete(reverse("student-archive-file-detail", args=[archive.id]))

    assert response.status_code == 204
    assert not StudentArchiveFile.objects.filter(pk=archive.pk).exists()


@pytest.mark.django_db
def test_supervisor_cannot_delete_archive_file(client, pi_user, student_profile):
    archive = StudentArchiveFile.objects.create(
        student=student_profile,
        file_type=StudentArchiveFile.FileType.PROPOSAL_REPORT,
        title="开题报告",
        file=ContentFile(b"proposal", name="proposal.txt"),
    )
    client.login(username="pi", password="pass12345")

    response = client.delete(reverse("student-archive-file-detail", args=[archive.id]))

    assert response.status_code == 403
    assert StudentArchiveFile.objects.filter(pk=archive.pk).exists()
