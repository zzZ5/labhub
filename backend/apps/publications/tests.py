import pytest
from django.urls import reverse

from apps.news.models import Visibility

from .models import Project, Publication


@pytest.mark.django_db
def test_public_publications_only(client):
    Publication.objects.create(title="公开论文", authors="A", journal="J", year=2026, visibility=Visibility.PUBLIC)
    Publication.objects.create(title="内部论文", authors="A", journal="J", year=2026, visibility=Visibility.MEMBERS)

    response = client.get(reverse("public-publication-list"))

    titles = [item["title"] for item in response.json()["results"]]
    assert "公开论文" in titles
    assert "内部论文" not in titles


@pytest.mark.django_db
def test_public_stats(client):
    Publication.objects.create(title="公开论文", authors="A", journal="J", year=2026)
    Project.objects.create(title="公开项目")

    response = client.get(reverse("public-publication-stats"))

    assert response.status_code == 200
    assert response.json()["publications"] == 1
    assert response.json()["projects"] == 1
