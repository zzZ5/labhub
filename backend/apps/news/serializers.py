from html import escape
from io import BytesIO
import base64
import mimetypes
import posixpath
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
        view = self.context.get("view")
        if getattr(view, "action", "") != "retrieve":
            return ""
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
                blocks.append(f"<p>{escape(text)}</p>")

            for blip in paragraph.findall(".//a:blip", namespace):
                relation_id = blip.attrib.get(f"{{{namespace['r']}}}embed")
                image_html = _image_html(archive, relationships, relation_id)
                if image_html:
                    blocks.append(image_html)

    return "\n".join(blocks)


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


def _image_html(archive, relationships, relation_id):
    if not relation_id:
        return ""
    target = relationships.get(relation_id)
    if not target:
        return ""
    image_path = target if target.startswith("word/") else posixpath.normpath(posixpath.join("word", target))
    if image_path.startswith("../"):
        return ""
    try:
        image_data = archive.read(image_path)
    except KeyError:
        return ""

    content_type = mimetypes.guess_type(image_path)[0] or "image/png"
    encoded = base64.b64encode(image_data).decode("ascii")
    return f'<figure><img src="data:{content_type};base64,{encoded}" alt="" /></figure>'
