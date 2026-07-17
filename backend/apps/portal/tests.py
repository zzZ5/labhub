import pytest
from django.urls import reverse

from .models import ResearchDirection, SiteSetting


@pytest.mark.django_db
def test_public_site_setting(client):
    SiteSetting.objects.create(site_name="LabHub", site_subtitle="生态系实验室", hero_subtitle="堆肥微生物过程")

    response = client.get(reverse("public-site-setting"))

    assert response.status_code == 200
    assert response.json()["site_name"] == "LabHub"
    assert response.json()["hero_subtitle"] == "堆肥微生物过程"
    assert "keywords" not in response.json()


@pytest.mark.django_db
def test_research_direction_only_active(client):
    ResearchDirection.objects.create(title="公开方向", slug="active", is_active=True)
    ResearchDirection.objects.create(title="隐藏方向", slug="inactive", is_active=False)

    response = client.get(reverse("public-research-direction-list"))

    titles = [item["title"] for item in response.json()]
    assert "公开方向" in titles
    assert "隐藏方向" not in titles
    assert all("keywords" not in item for item in response.json())
