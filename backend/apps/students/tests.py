from django.core.files.base import ContentFile
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.accounts.models import Role, RoleCode, UserRole

from .models import StudentArchiveFile, StudentProfile, StudentVisibility
from .services import can_view_student_profile

User = get_user_model()


@pytest.fixture
def student_user(db):
    user = User.objects.create_user(username="student", password="pass12345")
    user.profile.is_approved = True
    user.profile.save()
    role, _ = Role.objects.get_or_create(code=RoleCode.MASTER, defaults={"name": "硕士生"})
    UserRole.objects.get_or_create(user=user, role=role)
    return user


@pytest.fixture
def pi_user(db):
    user = User.objects.create_user(username="pi", password="pass12345")
    user.profile.is_approved = True
    user.profile.save()
    role, _ = Role.objects.get_or_create(code=RoleCode.PI, defaults={"name": "硕博导师"})
    UserRole.objects.get_or_create(user=user, role=role)
    return user


@pytest.fixture
def other_user(db):
    user = User.objects.create_user(username="other", password="pass12345")
    user.profile.is_approved = True
    user.profile.save()
    role, _ = Role.objects.get_or_create(code=RoleCode.MEMBER, defaults={"name": "课题组成员"})
    UserRole.objects.get_or_create(user=user, role=role)
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
        visibility=StudentVisibility.SUPERVISOR,
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
def test_member_cannot_view_supervisor_private_profile(client, other_user, student_profile):
    client.login(username="other", password="pass12345")

    response = client.get(reverse("student-profile-list"))

    assert response.status_code == 200
    assert response.json() == []


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
            "version": "v1.0",
            "visibility": StudentVisibility.SUPERVISOR,
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
            "version": "v1.0",
            "visibility": StudentVisibility.PRIVATE,
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
        visibility=StudentVisibility.SUPERVISOR,
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
        visibility=StudentVisibility.SUPERVISOR,
    )
    client.login(username="pi", password="pass12345")

    response = client.delete(reverse("student-archive-file-detail", args=[archive.id]))

    assert response.status_code == 403
    assert StudentArchiveFile.objects.filter(pk=archive.pk).exists()
