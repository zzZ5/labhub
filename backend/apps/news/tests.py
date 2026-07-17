from io import BytesIO
from zipfile import ZipFile

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.accounts.models import Role, RoleCode, UserRole

from .models import NewsArticle, NewsCategory, Visibility
from .serializers import sanitize_news_html

User = get_user_model()


def make_news_editor(username):
    user = User.objects.create_user(username=username, password="pass12345")
    user.profile.is_approved = True
    user.profile.save(update_fields=["is_approved"])
    role, _ = Role.objects.get_or_create(code=RoleCode.EDITOR, defaults={"name": "网站编辑"})
    UserRole.objects.create(user=user, role=role)
    return user


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


@pytest.mark.django_db
def test_school_lab_news_categories_are_complete(client):
    response = client.get(reverse("public-news-category-list"))

    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == [
        "组内动态",
        "学术交流",
        "科研进展",
        "成果荣誉",
        "招生招聘",
        "项目动态",
    ]
    assert NewsCategory.objects.filter(slug="project-related").exists()


def build_news_docx_with_image():
    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr(
            "word/document.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
 xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
 <w:body><w:p><w:r><w:t>堆肥微生物研究进展</w:t></w:r>
 <w:r><a:blip r:embed="rId1" /></w:r></w:p></w:body>
</w:document>""",
        )
        archive.writestr(
            "word/_rels/document.xml.rels",
            """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/figure.png" />
</Relationships>""",
        )
        archive.writestr("word/media/figure.png", b"\x89PNG\r\n\x1a\nLabHub")
    return buffer.getvalue()


@pytest.mark.django_db
def test_cms_word_news_extracts_inline_image_and_returns_processed_html(client):
    make_news_editor("news-editor")
    client.login(username="news-editor", password="pass12345")
    word_file = SimpleUploadedFile(
        "team-news.docx",
        build_news_docx_with_image(),
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

    response = client.post(
        reverse("cms-news-article-list"),
        {
            "title": "团队科研进展",
            "status": "published",
            "visibility": "public",
            "word_file": word_file,
        },
    )

    assert response.status_code == 201
    article = NewsArticle.objects.get(title="团队科研进展")
    assert "堆肥微生物研究进展" in article.word_html
    assert "<img" in article.word_html
    assert article.images.count() == 1
    assert article.cover_image

    detail = client.get(reverse("public-news-article-detail", args=[article.slug]))
    listing = client.get(reverse("public-news-article-list"))
    assert detail.status_code == 200
    assert "<img" in detail.json()["word_html"]
    assert listing.json()[0]["word_html"] == ""
