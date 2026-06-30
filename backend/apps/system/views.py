from django.db import connections
from django.db.utils import OperationalError
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import UserProfile
from apps.accounts.services import can_manage_accounts
from apps.documents.models import Document, DocumentDownloadLog, DocumentStatus
from apps.documents.services import visible_documents_for_user
from apps.instruments.models import Instrument
from apps.students.models import StudentArchiveFile, StudentProfile
from apps.students.services import visible_students_for_user


def backend_index(request):
    return HttpResponse(
        """
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>LabHub Backend</title>
    <style>
      body { margin: 0; font-family: Inter, "Noto Sans SC", "Microsoft YaHei", sans-serif; color: #2f3437; background: #f8f7f2; }
      main { max-width: 780px; margin: 12vh auto; padding: 36px; border: 1px solid #e5e7eb; border-radius: 14px; background: #fff; }
      h1 { margin: 0 0 10px; color: #1f3d2b; }
      p { color: #6b7280; line-height: 1.7; }
      a { display: inline-block; margin: 8px 10px 0 0; padding: 9px 14px; border-radius: 8px; color: #00873c; border: 1px solid #00873c; text-decoration: none; font-weight: 600; }
      a.primary { color: #fff; background: #00873c; }
    </style>
  </head>
  <body>
    <main>
      <h1>LabHub Backend</h1>
      <p>这是 LabHub 后端服务入口。公开门户和内部平台请访问前端 Vite 服务。</p>
      <a class="primary" href="http://localhost:5173/">打开前端</a>
      <a href="/api/health/">健康检查</a>
      <a href="/swagger/">API 文档</a>
      <a href="/admin/">Django Admin</a>
    </main>
  </body>
</html>
        """,
        content_type="text/html; charset=utf-8",
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    database_ok = True
    try:
        connections["default"].cursor()
    except OperationalError:
        database_ok = False

    status_code = 200 if database_ok else 503
    return Response(
        {
            "status": "ok" if database_ok else "degraded",
            "service": "labhub-backend",
            "database": "ok" if database_ok else "unavailable",
        },
        status=status_code,
    )


@ensure_csrf_cookie
@api_view(["GET"])
@permission_classes([AllowAny])
def csrf_token(request):
    return Response({"csrfToken": get_token(request)})


def _document_payload(document):
    return {
        "id": document.id,
        "title": document.title,
        "category_name": document.category.name if document.category else "未分类",
        "current_version": document.current_version or "v1.0",
        "visibility": document.visibility,
        "updated_at": document.updated_at,
    }


def _student_archive_payload(student):
    files = list(student.archive_files.all())
    return {
        "id": student.id,
        "name": student.name,
        "degree_type": student.degree_type,
        "grade": student.grade,
        "research_direction": student.research_direction,
        "file_count": len(files),
        "latest_file_title": files[0].title if files else "",
        "latest_uploaded_at": files[0].uploaded_at if files else None,
    }


def _download_payload(log):
    version_label = log.version.version if log.version else log.document.current_version
    return {
        "id": log.id,
        "document_title": log.document.title,
        "version_label": version_label or "当前版本",
        "downloaded_at": log.downloaded_at,
    }


def _instrument_payload(instrument):
    return {
        "id": instrument.id,
        "name": instrument.name,
        "room": instrument.room,
        "location_detail": instrument.location_detail,
        "status": instrument.status,
        "status_label": instrument.get_status_display(),
        "need_training": instrument.need_training,
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    user = request.user
    can_manage_users = can_manage_accounts(user)

    document_queryset = visible_documents_for_user(
        user,
        Document.objects.select_related("category").filter(status=DocumentStatus.ACTIVE),
    )
    student_queryset = (
        visible_students_for_user(
            user,
            StudentProfile.objects.select_related("user", "supervisor").prefetch_related("archive_files"),
        )
        .distinct()
        .order_by("-grade", "name")
    )

    instruments = Instrument.objects.all().order_by("sort_order", "name")
    instruments_needing_attention = instruments.filter(status__in=[Instrument.Status.MAINTENANCE, Instrument.Status.DISABLED])
    student_archive_count = StudentArchiveFile.objects.filter(student__in=student_queryset).count()
    pending_user_count = UserProfile.objects.filter(is_approved=False).count() if can_manage_users else 0

    todos = []
    if can_manage_users and pending_user_count:
        todos.append(
            {
                "title": "审核新成员账号",
                "detail": f"当前有 {pending_user_count} 个注册账号等待确认身份与角色。",
                "level": "warning",
                "target": "/members",
            }
        )
    instrument_attention_count = instruments_needing_attention.distinct().count()
    if instrument_attention_count:
        todos.append(
            {
                "title": "查看仪器设备状态",
                "detail": f"有 {instrument_attention_count} 台设备处于维护或停用状态，请按线下台账确认使用安排。",
                "level": "normal",
                "target": "/instruments",
            }
        )

    return Response(
        {
            "summary": [
                {"label": "待审核账号", "value": pending_user_count, "note": "仅管理员与硕博导师可见"},
                {"label": "设备需关注", "value": instrument_attention_count, "note": "维护或停用设备"},
                {"label": "可查阅资料", "value": document_queryset.count(), "note": "当前权限范围内"},
                {"label": "学生资料", "value": student_archive_count, "note": "开题报告、毕业论文等归档材料"},
            ],
            "instrument_status": [_instrument_payload(item) for item in instruments_needing_attention.distinct()[:5]],
            "latest_documents": [_document_payload(item) for item in document_queryset.order_by("-updated_at")[:5]],
            "todos": todos,
            "student_archives": [_student_archive_payload(item) for item in student_queryset[:5]],
            "recent_downloads": [
                _download_payload(item)
                for item in DocumentDownloadLog.objects.select_related("document", "version")
                .filter(user=user)
                .order_by("-downloaded_at")[:5]
            ],
        }
    )
