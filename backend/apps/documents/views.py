import base64
import mimetypes
import posixpath
import shutil
import subprocess
import tempfile
from html import escape
from io import BytesIO
from pathlib import Path
from urllib.parse import quote
from zipfile import BadZipFile, ZipFile
from xml.etree import ElementTree

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from apps.accounts.permissions import ApprovedMemberAccess

from .models import Document, DocumentCategory, DocumentDownloadLog, DocumentStatus, DocumentTag
from .responses import protected_file_response
from .serializers import DocumentCategorySerializer, DocumentDownloadLogSerializer, DocumentSerializer, DocumentTagSerializer, DocumentWriteSerializer
from .importers import import_documents_excel
from .services import (
    can_delete_document,
    can_download_document,
    can_edit_document,
    can_upload_document,
    can_view_document,
    visible_documents_for_user,
)
from apps.students.preview import is_office_preview_candidate

DOCX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
CONVERTIBLE_IMAGE_EXTENSIONS = {".emf", ".wmf", ".svg"}


def client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def is_docx_file(filename, content_type):
    return content_type == DOCX_CONTENT_TYPE or filename.lower().endswith(".docx")


def convert_embedded_image_to_png(image_data, filename):
    if Path(filename).suffix.lower() not in CONVERTIBLE_IMAGE_EXTENSIONS:
        return None
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        return None
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = Path(temp_dir) / Path(filename).name
        source_path.write_bytes(image_data)
        try:
            completed = subprocess.run(
                [soffice, "--headless", "--nologo", "--nofirststartwizard", "--convert-to", "png", "--outdir", temp_dir, str(source_path)],
                check=False,
                capture_output=True,
                timeout=20,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None
        output_path = source_path.with_suffix(".png")
        if completed.returncode != 0 or not output_path.exists():
            return None
        return output_path.read_bytes()


def docx_to_html(file_obj, title):
    data = file_obj.read()
    with ZipFile(BytesIO(data)) as archive:
        xml_content = archive.read("word/document.xml")
        rels_content = archive.read("word/_rels/document.xml.rels") if "word/_rels/document.xml.rels" in archive.namelist() else b""

    namespace = {
        "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    }
    root = ElementTree.fromstring(xml_content)
    blocks = []
    image_map = {}

    if rels_content:
        rels_root = ElementTree.fromstring(rels_content)
        rel_namespace = {"pr": "http://schemas.openxmlformats.org/package/2006/relationships"}
        with ZipFile(BytesIO(data)) as archive:
            for rel in rels_root.findall("pr:Relationship", rel_namespace):
                rel_id = rel.attrib.get("Id")
                target = rel.attrib.get("Target", "")
                rel_type = rel.attrib.get("Type", "")
                if not rel_id or "image" not in rel_type or not target:
                    continue
                media_path = posixpath.normpath(posixpath.join("word", target))
                if media_path not in archive.namelist():
                    continue
                image_data = archive.read(media_path)
                content_type = mimetypes.guess_type(media_path)[0] or ""
                if content_type not in {"image/png", "image/jpeg", "image/gif", "image/webp", "image/bmp"}:
                    image_data = convert_embedded_image_to_png(image_data, media_path)
                    if not image_data:
                        image_map[rel_id] = '<p class="image-note">这张图片暂不能在线显示，请下载原 Word 查看。</p>'
                        continue
                    content_type = "image/png"
                encoded = base64.b64encode(image_data).decode("ascii")
                image_map[rel_id] = f'<figure><img src="data:{content_type};base64,{encoded}" alt="Word 文档图片" /></figure>'

    def paragraph_text(paragraph):
        parts = [node.text or "" for node in paragraph.findall(".//w:t", namespace)]
        return "".join(parts).strip()

    def paragraph_html(paragraph):
        parts = []
        text = paragraph_text(paragraph)
        if text:
            parts.append(f"<p>{escape(text)}</p>")
        for blip in paragraph.findall(".//a:blip", namespace):
            rel_id = blip.attrib.get(f"{{{namespace['r']}}}embed") or blip.attrib.get(f"{{{namespace['r']}}}link")
            if rel_id and rel_id in image_map:
                parts.append(image_map[rel_id])
        return "".join(parts)

    def table_html(table):
        rows = []
        for row in table.findall("./w:tr", namespace):
            cells = []
            for cell in row.findall("./w:tc", namespace):
                content = "".join(filter(None, (paragraph_html(p) for p in cell.findall("./w:p", namespace))))
                cells.append(f"<td>{content}</td>")
            if cells:
                rows.append(f"<tr>{''.join(cells)}</tr>")
        if not rows:
            return ""
        return f"<table>{''.join(rows)}</table>"

    body = root.find("w:body", namespace)
    for child in list(body) if body is not None else []:
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "p":
            html = paragraph_html(child)
            if html:
                blocks.append(html)
        elif tag == "tbl":
            html = table_html(child)
            if html:
                blocks.append(html)

    body = "\n".join(blocks)
    if not body:
        paragraphs = []
        for paragraph in root.findall(".//w:p", namespace):
            text = paragraph_text(paragraph)
            if text:
                paragraphs.append(text)
        body = "\n".join(f"<p>{escape(paragraph)}</p>" for paragraph in paragraphs)
    if not body:
        body = '<p class="muted">该 Word 文档没有可提取的文本内容。</p>'

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>{escape(title)}</title>
  <style>
    :root {{
      color: #2f3437;
      background: #f5f7f6;
      font-family: "Noto Sans SC", "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
    }}
    body {{
      margin: 0;
      padding: 34px 18px 52px;
      background: #f5f7f6;
    }}
    article {{
      max-width: 860px;
      min-height: calc(100vh - 108px);
      margin: 0 auto;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 48px 58px;
      background: #fff;
      box-shadow: 0 14px 32px rgba(31, 61, 43, 0.08);
    }}
    h1 {{
      margin: 0 0 26px;
      color: #1f3d2b;
      font-size: 26px;
      font-weight: 650;
      line-height: 1.45;
    }}
    p {{
      margin: 0 0 16px;
      font-size: 16px;
      line-height: 1.85;
      white-space: pre-wrap;
    }}
    table {{
      width: 100%;
      margin: 18px 0 22px;
      border-collapse: collapse;
      font-size: 15px;
      line-height: 1.6;
    }}
    td {{
      border: 1px solid #e5e7eb;
      padding: 9px 11px;
      vertical-align: top;
      word-break: break-word;
    }}
    tr:first-child td {{
      background: #eaf5ee;
      color: #1f3d2b;
      font-weight: 650;
    }}
    figure {{
      margin: 20px 0 24px;
      text-align: center;
    }}
    img {{
      max-width: 100%;
      height: auto;
      border-radius: 8px;
      background: #fff;
    }}
    .image-note {{
      border: 1px dashed #c8d3cc;
      border-radius: 8px;
      padding: 12px 14px;
      background: #f8f7f2;
      color: #6b7280;
      font-size: 14px;
      text-align: center;
    }}
    .muted {{
      color: #6b7280;
    }}
    @media (max-width: 720px) {{
      body {{
        padding: 14px;
      }}
      article {{
        padding: 26px 20px;
      }}
    }}
  </style>
</head>
<body>
  <article>
    <h1>{escape(title)}</h1>
    {body}
  </article>
</body>
</html>"""


class DocumentCategoryViewSet(ReadOnlyModelViewSet):
    queryset = DocumentCategory.objects.all()
    serializer_class = DocumentCategorySerializer
    permission_classes = [ApprovedMemberAccess]
    lookup_field = "slug"


class DocumentTagViewSet(ReadOnlyModelViewSet):
    queryset = DocumentTag.objects.all()
    serializer_class = DocumentTagSerializer
    permission_classes = [ApprovedMemberAccess]
    lookup_field = "slug"


class DocumentViewSet(ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [ApprovedMemberAccess]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["category__slug", "status"]
    search_fields = ["title", "description", "tags__name"]

    def get_permissions(self):
        if self.action in {"preview", "download"}:
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return DocumentWriteSerializer
        return DocumentSerializer

    def get_queryset(self):
        queryset = (
            Document.objects.filter(status=DocumentStatus.ACTIVE)
            .select_related("category", "owner", "uploaded_by", "uploaded_by__profile")
            .prefetch_related("tags")
            .order_by("created_at", "id")
        )
        return visible_documents_for_user(self.request.user, queryset)

    def create(self, request, *args, **kwargs):
        if not can_upload_document(request.user):
            return Response({"detail": "无权维护资料库。"}, status=status.HTTP_403_FORBIDDEN)
        response = super().create(request, *args, **kwargs)
        document = Document.objects.select_related("category", "uploaded_by", "uploaded_by__profile").get(pk=response.data["id"])
        return Response(DocumentSerializer(document, context={"request": request}).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        document = self.get_object()
        if not can_edit_document(request.user, document):
            return Response({"detail": "只能维护自己上传的资料。"}, status=status.HTTP_403_FORBIDDEN)
        response = super().update(request, *args, **kwargs)
        document = Document.objects.select_related("category", "uploaded_by", "uploaded_by__profile").get(pk=response.data["id"])
        return Response(DocumentSerializer(document, context={"request": request}).data)

    def destroy(self, request, *args, **kwargs):
        document = self.get_object()
        if not can_delete_document(request.user, document):
            return Response({"detail": "只能删除自己上传的资料。"}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        document = self.get_object()
        if not can_view_document(request.user, document):
            return Response({"detail": "无权查看该资料。"}, status=status.HTTP_403_FORBIDDEN)
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=["post"], url_path="import-excel")
    def import_excel(self, request):
        if not can_upload_document(request.user):
            return Response({"detail": "无权维护资料库。"}, status=status.HTTP_403_FORBIDDEN)

        excel_file = request.FILES.get("file")
        archive_file = request.FILES.get("archive")
        if not excel_file:
            return Response({"detail": "请上传 .xlsx 格式的资料清单。"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = import_documents_excel(excel_file, archive_file=archive_file, user=request.user)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        document = get_object_or_404(
            Document.objects.all(),
            pk=pk,
            status=DocumentStatus.ACTIVE,
        )
        if not request.user.is_authenticated:
            return Response({"detail": "请先登录。"}, status=status.HTTP_401_UNAUTHORIZED)
        if not can_download_document(request.user, document):
            return Response({"detail": "无权下载该资料。"}, status=status.HTTP_403_FORBIDDEN)

        if not document.file:
            return Response({"detail": "当前资料没有可下载文件。"}, status=status.HTTP_404_NOT_FOUND)

        DocumentDownloadLog.objects.create(
            document=document,
            user=request.user,
            ip_address=client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        filename = document.original_filename or Path(document.file.name).name
        return protected_file_response(document.file, filename, as_attachment=True)

    @action(detail=True, methods=["get"], url_path="preview")
    def preview(self, request, pk=None):
        document = get_object_or_404(
            Document.objects.all(),
            pk=pk,
            status=DocumentStatus.ACTIVE,
        )
        if not request.user.is_authenticated:
            return Response({"detail": "请先登录。"}, status=status.HTTP_401_UNAUTHORIZED)
        if not can_view_document(request.user, document):
            return Response({"detail": "无权查看该资料。"}, status=status.HTTP_403_FORBIDDEN)

        if not document.file:
            return Response({"detail": "当前资料没有可查看文件。"}, status=status.HTTP_404_NOT_FOUND)

        filename = document.original_filename or Path(document.file.name).name
        if document.preview_pdf:
            response = protected_file_response(
                document.preview_pdf,
                Path(filename).stem + ".pdf",
                as_attachment=False,
                content_type="application/pdf",
            )
            response["X-Frame-Options"] = "SAMEORIGIN"
            response["X-Content-Type-Options"] = "nosniff"
            return response

        content_type = document.file_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
        if is_docx_file(filename, content_type):
            try:
                with document.file.open("rb") as file_obj:
                    html = docx_to_html(file_obj, document.title)
            except (BadZipFile, KeyError, ElementTree.ParseError):
                return Response({"detail": "该 Word 文件暂不能在线预览，请下载查看。"}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
            response = HttpResponse(html, content_type="text/html; charset=utf-8")
            response["Content-Disposition"] = f"inline; filename*=UTF-8''{quote(filename)}"
            response["X-Frame-Options"] = "SAMEORIGIN"
            response["X-Content-Type-Options"] = "nosniff"
            return response

        if is_office_preview_candidate(filename) and document.preview_status == "failed":
            detail = document.preview_error or "PDF 预览生成失败，请下载原文件查看。"
            return Response({"detail": detail}, status=status.HTTP_409_CONFLICT)
        if is_office_preview_candidate(filename) and document.preview_status == "pending":
            return Response({"detail": "PDF 预览正在生成，请稍后再试。"}, status=status.HTTP_202_ACCEPTED)

        response = protected_file_response(document.file, filename, as_attachment=False, content_type=content_type)
        response["X-Frame-Options"] = "SAMEORIGIN"
        response["X-Content-Type-Options"] = "nosniff"
        return response


class DocumentDownloadLogViewSet(ReadOnlyModelViewSet):
    serializer_class = DocumentDownloadLogSerializer
    permission_classes = [ApprovedMemberAccess]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return DocumentDownloadLog.objects.select_related("document", "user")
        return DocumentDownloadLog.objects.filter(user=self.request.user).select_related("document", "user")
