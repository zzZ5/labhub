import pytest
from django.urls import reverse

from apps.news.models import Visibility

from .models import Award, Patent, Project, Publication


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


@pytest.mark.django_db
def test_publication_search_and_pagination(client):
    for index in range(15):
        Publication.objects.create(
            title=f"堆肥微生物论文 {index:02d}",
            authors="中农雨磷团队",
            journal="Bioresource Technology",
            year=2026 - (index % 2),
            doi=f"10.1000/labhub.{index}",
            visibility=Visibility.PUBLIC,
        )
    Publication.objects.create(title="不匹配论文", authors="其他团队", journal="Other", year=2024)

    page_response = client.get(reverse("public-publication-list"), {"search": "堆肥微生物", "page": 2})
    doi_response = client.get(reverse("public-publication-list"), {"search": "10.1000/labhub.7"})

    assert page_response.status_code == 200
    assert page_response.json()["count"] == 15
    assert len(page_response.json()["results"]) == 3
    assert doi_response.json()["count"] == 1
    assert doi_response.json()["results"][0]["title"] == "堆肥微生物论文 07"


@pytest.mark.django_db
def test_publication_year_filter(client):
    Publication.objects.create(title="2026 年论文", authors="A", journal="J", year=2026)
    Publication.objects.create(title="2025 年论文", authors="A", journal="J", year=2025)

    response = client.get(reverse("public-publication-list"), {"year": 2025})

    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["results"][0]["title"] == "2025 年论文"


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("route_name", "model", "create_kwargs", "search"),
    [
        ("public-project-list", Project, {"title": "农业废弃物项目", "project_number": "CAU-2026"}, "CAU-2026"),
        ("public-patent-list", Patent, {"title": "堆肥菌剂专利", "patent_number": "CN20260001"}, "CN20260001"),
        ("public-award-list", Award, {"title": "资源循环成果奖", "award_level": "一等奖"}, "一等奖"),
    ],
)
def test_other_public_results_support_search(client, route_name, model, create_kwargs, search):
    model.objects.create(**create_kwargs)

    response = client.get(reverse(route_name), {"search": search})

    assert response.status_code == 200
    assert response.json()["count"] == 1
