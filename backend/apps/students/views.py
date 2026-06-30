import mimetypes
from pathlib import Path
from urllib.parse import quote

from django.http import FileResponse, HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.documents.views import docx_to_html, is_docx_file

from .models import StudentArchiveFile, StudentProfile
from .preview import is_office_preview_candidate, refresh_archive_preview_pdf
from .serializers import (
    StudentArchiveFileSerializer,
    StudentProfileSerializer,
)
from .services import (
    can_delete_archive_file,
    can_delete_student_profile,
    can_edit_student_profile,
    can_manage_student_archives,
    can_view_archive_file,
    visible_students_for_user,
)


class StudentProfileViewSet(viewsets.ModelViewSet):
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = StudentProfile.objects.select_related("user", "supervisor", "supervisor__profile").prefetch_related("archive_files")
        return visible_students_for_user(self.request.user, queryset).distinct()

    def perform_create(self, serializer):
        target_user = serializer.validated_data.get("user")
        if not (can_manage_student_archives(self.request.user) or target_user == self.request.user):
            raise PermissionDenied("无权为其他成员创建学生档案。")
        serializer.save()

    def update(self, request, *args, **kwargs):
        student = self.get_object()
        if not can_edit_student_profile(request.user, student):
            return Response({"detail": "无权修改该学生档案。"}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        student = self.get_object()
        if not can_delete_student_profile(request.user, student):
            return Response({"detail": "无权删除该学生档案。"}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        student = StudentProfile.objects.filter(user=request.user).first()
        if not student:
            return Response({"detail": "当前账号没有学生档案。"}, status=status.HTTP_404_NOT_FOUND)
        return Response(StudentProfileSerializer(student, context={"request": request}).data)


class StudentArchiveFileViewSet(viewsets.ModelViewSet):
    serializer_class = StudentArchiveFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        students = visible_students_for_user(self.request.user, StudentProfile.objects.all())
        queryset = StudentArchiveFile.objects.filter(student__in=students).select_related("student", "uploaded_by")
        return queryset

    def perform_create(self, serializer):
        student = serializer.validated_data["student"]
        if not can_edit_student_profile(self.request.user, student):
            raise PermissionDenied("无权上传该学生材料。")
        archive_file = serializer.save(uploaded_by=self.request.user)
        refresh_archive_preview_pdf(archive_file)

    def retrieve(self, request, *args, **kwargs):
        archive_file = self.get_object()
        if not can_view_archive_file(request.user, archive_file):
            return Response({"detail": "无权查看该材料。"}, status=status.HTTP_403_FORBIDDEN)
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=["get"], url_path="preview")
    def preview(self, request, pk=None):
        archive_file = self.get_object()
        if not can_view_archive_file(request.user, archive_file):
            return Response({"detail": "无权查看该材料。"}, status=status.HTTP_403_FORBIDDEN)
        if not archive_file.file:
            return Response({"detail": "当前材料没有可查看文件。"}, status=status.HTTP_404_NOT_FOUND)

        filename = archive_file.original_filename or Path(archive_file.file.name).name
        if archive_file.preview_pdf:
            response = FileResponse(archive_file.preview_pdf.open("rb"), as_attachment=False, content_type="application/pdf")
            response["Content-Disposition"] = f"inline; filename*=UTF-8''{quote(Path(filename).stem + '.pdf')}"
            response["X-Frame-Options"] = "SAMEORIGIN"
            response["X-Content-Type-Options"] = "nosniff"
            return response

        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        if is_office_preview_candidate(filename) and archive_file.preview_status == "failed":
            detail = archive_file.preview_error or "PDF 预览生成失败，请下载原文件查看。"
            return Response({"detail": detail}, status=status.HTTP_409_CONFLICT)
        if is_office_preview_candidate(filename) and archive_file.preview_status == "pending":
            return Response({"detail": "PDF 预览正在生成，请稍后再试。"}, status=status.HTTP_202_ACCEPTED)
        if is_docx_file(filename, content_type):
            try:
                with archive_file.file.open("rb") as file_obj:
                    html = docx_to_html(file_obj, archive_file.title)
            except Exception:
                return Response({"detail": "该 Word 文件暂不能在线预览，请下载查看。"}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
            response = HttpResponse(html, content_type="text/html; charset=utf-8")
        else:
            response = FileResponse(archive_file.file.open("rb"), as_attachment=False, content_type=content_type)
        response["Content-Disposition"] = f"inline; filename*=UTF-8''{quote(filename)}"
        response["X-Frame-Options"] = "SAMEORIGIN"
        response["X-Content-Type-Options"] = "nosniff"
        return response

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        archive_file = self.get_object()
        if not can_view_archive_file(request.user, archive_file):
            return Response({"detail": "无权下载该材料。"}, status=status.HTTP_403_FORBIDDEN)
        if not archive_file.file:
            return Response({"detail": "当前材料没有可下载文件。"}, status=status.HTTP_404_NOT_FOUND)

        filename = archive_file.original_filename or Path(archive_file.file.name).name
        response = FileResponse(archive_file.file.open("rb"), as_attachment=True)
        response["Content-Disposition"] = f"attachment; filename*=UTF-8''{quote(filename)}"
        return response

    def destroy(self, request, *args, **kwargs):
        archive_file = self.get_object()
        if not can_delete_archive_file(request.user, archive_file):
            return Response({"detail": "无权删除该学生材料。"}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
