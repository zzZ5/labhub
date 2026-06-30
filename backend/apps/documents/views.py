import mimetypes
from html import escape
from io import BytesIO
from pathlib import Path
from urllib.parse import quote
from zipfile import BadZipFile, ZipFile
from xml.etree import ElementTree

from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import Document, DocumentCategory, DocumentDownloadLog, DocumentStatus, DocumentTag, DocumentVersion
from .serializers import DocumentCategorySerializer, DocumentDownloadLogSerializer, DocumentSerializer, DocumentTagSerializer, DocumentWriteSerializer
from .services import can_download_document, can_manage_documents, can_view_document, visible_documents_for_user
from apps.students.preview import is_office_preview_candidate

DOCX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def is_docx_file(filename, content_type):
    return content_type == DOCX_CONTENT_TYPE or filename.lower().endswith(".docx")


def docx_to_html(file_obj, title):
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
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"


class DocumentTagViewSet(ReadOnlyModelViewSet):
    queryset = DocumentTag.objects.all()
    serializer_class = DocumentTagSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"


class DocumentViewSet(ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["category__slug", "visibility", "status"]
    search_fields = ["title", "description", "tags__name"]

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return DocumentWriteSerializer
        return DocumentSerializer

    def get_queryset(self):
        queryset = (
            Document.objects.filter(status=DocumentStatus.ACTIVE)
            .select_related("category", "owner", "maintainer")
            .prefetch_related("tags", "versions", "permissions", "permissions__role")
        )
        return visible_documents_for_user(self.request.user, queryset)

    def create(self, request, *args, **kwargs):
        if not can_manage_documents(request.user):
            return Response({"detail": "无权维护资料库。"}, status=status.HTTP_403_FORBIDDEN)
        response = super().create(request, *args, **kwargs)
        document = Document.objects.select_related("category").prefetch_related("versions").get(pk=response.data["id"])
        return Response(DocumentSerializer(document, context={"request": request}).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        if not can_manage_documents(request.user):
            return Response({"detail": "无权维护资料库。"}, status=status.HTTP_403_FORBIDDEN)
        response = super().update(request, *args, **kwargs)
        document = Document.objects.select_related("category").prefetch_related("versions").get(pk=response.data["id"])
        return Response(DocumentSerializer(document, context={"request": request}).data)

    def destroy(self, request, *args, **kwargs):
        if not can_manage_documents(request.user):
            return Response({"detail": "无权维护资料库。"}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        document = self.get_object()
        if not can_view_document(request.user, document):
            return Response({"detail": "无权查看该资料。"}, status=status.HTTP_403_FORBIDDEN)
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        document = get_object_or_404(
            Document.objects.prefetch_related("versions", "permissions", "permissions__role"),
            pk=pk,
            status=DocumentStatus.ACTIVE,
        )
        if not request.user.is_authenticated:
            return Response({"detail": "请先登录。"}, status=status.HTTP_401_UNAUTHORIZED)
        if not can_download_document(request.user, document):
            return Response({"detail": "无权下载该资料。"}, status=status.HTTP_403_FORBIDDEN)

        version_id = request.query_params.get("version")
        version_queryset = document.versions.all()
        version = (
            get_object_or_404(version_queryset, pk=version_id)
            if version_id
            else version_queryset.filter(is_current=True).order_by("-uploaded_at").first()
        )
        if not version or not version.file:
            return Response({"detail": "当前资料没有可下载文件。"}, status=status.HTTP_404_NOT_FOUND)

        DocumentDownloadLog.objects.create(
            document=document,
            version=version,
            user=request.user,
            ip_address=client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        filename = version.original_filename or Path(version.file.name).name
        response = FileResponse(version.file.open("rb"), as_attachment=True)
        response["Content-Disposition"] = f"attachment; filename*=UTF-8''{quote(filename)}"
        return response

    @action(detail=True, methods=["get"], url_path="preview")
    def preview(self, request, pk=None):
        document = get_object_or_404(
            Document.objects.prefetch_related("versions", "permissions", "permissions__role"),
            pk=pk,
            status=DocumentStatus.ACTIVE,
        )
        if not request.user.is_authenticated:
            return Response({"detail": "请先登录。"}, status=status.HTTP_401_UNAUTHORIZED)
        if not can_view_document(request.user, document):
            return Response({"detail": "无权查看该资料。"}, status=status.HTTP_403_FORBIDDEN)

        version_id = request.query_params.get("version")
        version_queryset = document.versions.all()
        version = (
            get_object_or_404(version_queryset, pk=version_id)
            if version_id
            else version_queryset.filter(is_current=True).order_by("-uploaded_at").first()
        )
        if not version or not version.file:
            return Response({"detail": "当前资料没有可查看文件。"}, status=status.HTTP_404_NOT_FOUND)

        filename = version.original_filename or Path(version.file.name).name
        if version.preview_pdf:
            response = FileResponse(version.preview_pdf.open("rb"), as_attachment=False, content_type="application/pdf")
            response["Content-Disposition"] = f"inline; filename*=UTF-8''{quote(Path(filename).stem + '.pdf')}"
            response["X-Frame-Options"] = "SAMEORIGIN"
            response["X-Content-Type-Options"] = "nosniff"
            return response

        content_type = version.file_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
        if is_office_preview_candidate(filename) and version.preview_status == "failed":
            detail = version.preview_error or "PDF 预览生成失败，请下载原文件查看。"
            return Response({"detail": detail}, status=status.HTTP_409_CONFLICT)
        if is_office_preview_candidate(filename) and version.preview_status == "pending":
            return Response({"detail": "PDF 预览正在生成，请稍后再试。"}, status=status.HTTP_202_ACCEPTED)
        if is_docx_file(filename, content_type):
            try:
                with version.file.open("rb") as file_obj:
                    html = docx_to_html(file_obj, document.title)
            except (BadZipFile, KeyError, ElementTree.ParseError):
                return Response({"detail": "该 Word 文件暂不能在线预览，请下载查看。"}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
            response = HttpResponse(html, content_type="text/html; charset=utf-8")
            response["Content-Disposition"] = f"inline; filename*=UTF-8''{quote(filename)}"
            response["X-Frame-Options"] = "SAMEORIGIN"
            response["X-Content-Type-Options"] = "nosniff"
            return response

        response = FileResponse(version.file.open("rb"), as_attachment=False, content_type=content_type)
        response["Content-Disposition"] = f"inline; filename*=UTF-8''{quote(filename)}"
        response["X-Frame-Options"] = "SAMEORIGIN"
        response["X-Content-Type-Options"] = "nosniff"
        return response


class DocumentDownloadLogViewSet(ReadOnlyModelViewSet):
    serializer_class = DocumentDownloadLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return DocumentDownloadLog.objects.select_related("document", "version", "user")
        return DocumentDownloadLog.objects.filter(user=self.request.user).select_related("document", "version", "user")
