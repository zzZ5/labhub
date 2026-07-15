import pytest
from django.urls import reverse

from .models import NewsArticle, Visibility
from .serializers import sanitize_news_html


def test_news_html_sanitizer_keeps_article_formatting_and_removes_scripts():
    html = (
        '<h2 style="text-align: center">标题</h2>'
        '<p><strong>正文</strong><script>alert(1)</script></p>'
        '<img src="/media/news/image.jpg" onerror="alert(2)" />'
        '<a href="javascript:alert(3)">链接</a>'
    )

    cleaned = sanitize_news_html(html)

    assert '<h2 style="text-align: center;">标题</h2>' in cleaned
    assert "<strong>正文</strong>" in cleaned
    assert 'src="/media/news/image.jpg"' in cleaned
    assert "script" not in cleaned
    assert "onerror" not in cleaned
    assert "javascript:" not in cleaned


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
