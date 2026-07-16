from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from apps.accounts.permissions import ApprovedMemberAccess

from .importers import import_instruments_from_excel
from .models import Instrument, InstrumentCategory, InstrumentFaultReport, InstrumentMaintenanceRecord, InstrumentTrainingRecord
from .serializers import (
    InstrumentCategorySerializer,
    InstrumentFaultReportSerializer,
    InstrumentMaintenanceRecordSerializer,
    InstrumentSerializer,
    InstrumentTrainingRecordSerializer,
)


class InstrumentCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InstrumentCategory.objects.all()
    serializer_class = InstrumentCategorySerializer
    permission_classes = [ApprovedMemberAccess]
    lookup_field = "slug"


def can_manage_instruments(user):
    from .services import user_can_manage_instrument

    return user_can_manage_instrument(user)


class InstrumentViewSet(viewsets.ModelViewSet):
    queryset = Instrument.objects.select_related("category", "manager", "manager__profile").prefetch_related("training_records")
    serializer_class = InstrumentSerializer
    permission_classes = [ApprovedMemberAccess]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_queryset(self):
        return super().get_queryset()

    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)

    def update(self, request, *args, **kwargs):
        if not can_manage_instruments(request.user):
            return Response({"detail": "无权维护仪器台账。"}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if not can_manage_instruments(request.user):
            return Response({"detail": "无权维护仪器台账。"}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not can_manage_instruments(request.user):
            return Response({"detail": "无权维护仪器台账。"}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=["post"], url_path="import-excel")
    def import_excel(self, request):
        if not can_manage_instruments(request.user):
            return Response({"detail": "无权维护仪器台账。"}, status=status.HTTP_403_FORBIDDEN)
        upload = request.FILES.get("file")
        if not upload:
            return Response({"detail": "请上传 Excel 文件。"}, status=status.HTTP_400_BAD_REQUEST)
        if not upload.name.lower().endswith(".xlsx"):
            return Response({"detail": "仅支持 .xlsx 文件。"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            result = import_instruments_from_excel(upload, uploaded_by=request.user)
        except Exception:
            return Response({"detail": "Excel 解析失败，请确认包含“仪器名称、状态、详细位置、设备图片、使用说明”等列。"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)


class InstrumentTrainingRecordViewSet(viewsets.ModelViewSet):
    queryset = InstrumentTrainingRecord.objects.select_related("instrument", "user", "user__profile", "trainer")
    serializer_class = InstrumentTrainingRecordSerializer
    permission_classes = [ApprovedMemberAccess]

    def perform_create(self, serializer):
        serializer.save(trainer=self.request.user)


class InstrumentMaintenanceRecordViewSet(viewsets.ModelViewSet):
    queryset = InstrumentMaintenanceRecord.objects.select_related("instrument", "maintainer")
    serializer_class = InstrumentMaintenanceRecordSerializer
    permission_classes = [ApprovedMemberAccess]

    def perform_create(self, serializer):
        serializer.save(maintainer=self.request.user)


class InstrumentFaultReportViewSet(viewsets.ModelViewSet):
    serializer_class = InstrumentFaultReportSerializer
    permission_classes = [ApprovedMemberAccess]

    def get_queryset(self):
        return InstrumentFaultReport.objects.select_related("instrument", "reporter", "handled_by")

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)
