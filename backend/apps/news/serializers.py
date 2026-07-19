from html import escape
from io import BytesIO
import posixpath
from zipfile import BadZipFile, ZipFile
from xml.etree import ElementTree

from rest_framework import serializers
from apps.system.serializer_fields import file_field_size
from apps.system.rich_text import sanitize_rich_text_html

from .models import NewsArticle, NewsCategory, NewsImage, NewsTag


def sanitize_news_html(value):
    return sanitize_rich_text_html(value)


class NewsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsCategory
        fields = ["id", "name", "slug", "description", "sort_order"]


class NewsTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsTag
        fields = ["id", "name", "slug"]


class NewsImageSerializer(serializers.ModelSerializer):
    image_size = serializers.SerializerMethodField()

    class Meta:
        model = NewsImage
        fields = ["id", "image", "image_size", "caption", "sort_order"]

    def get_image_size(self, obj):
        return file_field_size(obj.image)


class NewsArticleSerializer(serializers.ModelSerializer):
    category = NewsCategorySerializer(read_only=True)
    tags = NewsTagSerializer(many=True, read_only=True)
    images = NewsImageSerializer(many=True, read_only=True)
    cover_image_size = serializers.SerializerMethodField()
    word_file_size = serializers.SerializerMethodField()

    class Meta:
        model = NewsArticle
        fields = [
            "id",
            "title",
            "slug",
            "summary",
            "content",
            "cover_image",
            "cover_image_size",
            "word_file",
            "word_file_size",
            "word_html",
            "category",
            "tags",
            "images",
            "event_date",
            "location",
            "is_pinned",
            "published_at",
            "view_count",
            "created_at",
            "updated_at",
    ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["content"] = sanitize_news_html(data.get("content"))
        data["word_html"] = sanitize_news_html(data.get("word_html"))
        view = self.context.get("view")
        if getattr(view, "action", "") != "retrieve":
            data["word_html"] = ""
        return data

    def get_cover_image_size(self, obj):
        return file_field_size(obj.cover_image)

    def get_word_file_size(self, obj):
        return file_field_size(obj.word_file)

def parse_docx_blocks(file_obj):
    data = file_obj.read()
    with ZipFile(BytesIO(data)) as archive:
        xml_content = archive.read("word/document.xml")
        relationships = _read_document_relationships(archive)
        namespace = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
            "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
            "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        }
        root = ElementTree.fromstring(xml_content)
        blocks = []
        for paragraph in root.findall(".//w:p", namespace):
            parts = [node.text or "" for node in paragraph.findall(".//w:t", namespace)]
            text = "".join(parts).strip()
            if text:
                blocks.append(("text", text))

            for blip in paragraph.findall(".//a:blip", namespace):
                relation_id = blip.attrib.get(f"{{{namespace['r']}}}embed")
                target = relationships.get(relation_id)
                if not target:
                    continue
                image_path = target if target.startswith("word/") else posixpath.normpath(posixpath.join("word", target))
                if not image_path.startswith("../"):
                    blocks.append(("image", image_path))

    return blocks


def render_docx_blocks(blocks, image_urls=None):
    image_urls = image_urls or {}
    html_blocks = []
    for kind, value in blocks:
        if kind == "text":
            html_blocks.append(f"<p>{escape(value)}</p>")
        elif kind == "image" and value in image_urls:
            html_blocks.append(f'<figure><img src="{escape(image_urls[value])}" alt="" /></figure>')
    return "\n".join(html_blocks)


def docx_to_html_fragment(file_obj):
    return render_docx_blocks(parse_docx_blocks(file_obj))


def _read_document_relationships(archive):
    try:
        rels_xml = archive.read("word/_rels/document.xml.rels")
    except KeyError:
        return {}

    namespace = {"rel": "http://schemas.openxmlformats.org/package/2006/relationships"}
    root = ElementTree.fromstring(rels_xml)
    relationships = {}
    for rel in root.findall("rel:Relationship", namespace):
        rel_id = rel.attrib.get("Id")
        target = rel.attrib.get("Target", "")
        rel_type = rel.attrib.get("Type", "")
        if rel_id and target and rel_type.endswith("/image"):
            relationships[rel_id] = target
    return relationships


def extract_docx_images(file_obj):
    data = file_obj.read()
    images = []
    with ZipFile(BytesIO(data)) as archive:
        relationships = _read_document_relationships(archive)
        seen_paths = set()
        for target in relationships.values():
            image_path = target if target.startswith("word/") else posixpath.normpath(posixpath.join("word", target))
            if image_path.startswith("../") or image_path in seen_paths:
                continue
            seen_paths.add(image_path)
            try:
                images.append((image_path, posixpath.basename(image_path), archive.read(image_path)))
            except KeyError:
                continue
    return images
