import pytest
from django.urls import reverse

from .models import Member


@pytest.mark.django_db
def test_public_members_only(client):
    Member.objects.create(name="公开成员", role_type=Member.RoleType.PHD, is_public=True)
    Member.objects.create(name="隐藏成员", role_type=Member.RoleType.MASTER, is_public=False)

    response = client.get(reverse("public-member-list"))

    names = [item["name"] for item in response.json()]
    assert response.status_code == 200
    assert "公开成员" in names
    assert "隐藏成员" not in names
