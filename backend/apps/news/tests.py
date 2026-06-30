import pytest
from django.urls import reverse

from .models import NewsArticle, Visibility


@pytest.mark.django_db
def test_public_news_filters_visibility_and_status(client):
    NewsArticle.objects.create(
        title="公开新闻",
        slug="public-news",
        content="content",
        visibility=Visibility.PUBLIC,
        status=NewsArticle.Status.PUBLISHED,
    )
    NewsArticle.objects.create(
        title="内部新闻",
        slug="internal-news",
        content="content",
        visibility=Visibility.MEMBERS,
        status=NewsArticle.Status.PUBLISHED,
    )
    NewsArticle.objects.create(
        title="草稿新闻",
        slug="draft-news",
        content="content",
        visibility=Visibility.PUBLIC,
        status=NewsArticle.Status.DRAFT,
    )

    response = client.get(reverse("public-news-article-list"))

    titles = [item["title"] for item in response.json()]
    assert "公开新闻" in titles
    assert "内部新闻" not in titles
    assert "草稿新闻" not in titles
