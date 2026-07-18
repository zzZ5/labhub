import pytest
from datetime import date
from django.urls import reverse

from .models import Member


@pytest.mark.django_db
def test_public_members_only(client):
    Member.objects.create(name="公开成员", role_type="博士研究生", sort_order=1)
    Member.objects.create(name="隐藏成员", role_type="硕士研究生", sort_order=0)

    response = client.get(reverse("public-member-list"))

    names = [item["name"] for item in response.json()]
    assert response.status_code == 200
    assert "公开成员" in names
    assert "隐藏成员" not in names


@pytest.mark.django_db
def test_public_members_prioritize_active_then_role(client):
    Member.objects.create(name="历史导师", role_type="硕博导师", graduation_date=date(2025, 7, 1), sort_order=1)
    Member.objects.create(name="在组硕士", role_type="硕士生", sort_order=4)
    Member.objects.create(name="在组博士", role_type="博士生", sort_order=3)
    Member.objects.create(name="在组博士后", role_type="博士后", sort_order=2)
    Member.objects.create(name="在组导师", role_type="硕博导师", sort_order=5)

    response = client.get(reverse("public-member-list"))

    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == [
        "在组导师",
        "在组博士后",
        "在组博士",
        "在组硕士",
        "历史导师",
    ]
