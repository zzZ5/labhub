from html import escape
from io import BytesIO
from zipfile import BadZipFile, ZipFile
from xml.etree import ElementTree

from rest_framework import serializers

from .models import NewsArticle, NewsCategory, NewsImage, NewsTag


class NewsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsCategory
        fields = ["id", "name", "slug", "description", "sort_order"]


class NewsTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsTag
        fields = ["id", "name", "slug"]


class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImage
        fields = ["id", "image", "caption", "sort_order"]


class NewsArticleSerializer(serializers.ModelSerializer):
    category = NewsCategorySerializer(read_only=True)
    tags = NewsTagSerializer(many=True, read_only=True)
    images = NewsImageSerializer(many=True, read_only=True)
    word_html = serializers.SerializerMethodField()

    class Meta:
        model = NewsArticle
        fields = [
            "id",
            "title",
            "slug",
            "summary",
            "content",
            "cover_image",
            "word_file",
            "word_html",
            "category",
            "tags",
            "images",
            "event_date",
            "location",
            "is_pinned",
            "created_at",
            "updated_at",
        ]

    def get_word_html(self, obj):
        if not obj.word_file:
            return ""
        try:
            with obj.word_file.open("rb") as file_obj:
                return docx_to_html_fragment(file_obj)
        except (BadZipFile, KeyError, ElementTree.ParseError, OSError):
            return ""


def docx_to_html_fragment(file_obj):
    data = file_obj.read()
    with ZipFile(BytesIO(data)) as archive:
        xml_content = archive.read("word/document.xml")

    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    root = ElementTree.fromstring(xml_content)
    paragraphs = []
    for paragraph in root.findall(".//w:p", namespace):
        parts = [node.text or "" for node in paragraph.findall(".//w:t", namespace)]
        text = "".join(parts).strip()
        if text:
            paragraphs.append(text)
    return "\n".join(f"<p>{escape(paragraph)}</p>" for paragraph in paragraphs)
