from rest_framework import viewsets
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import RoleCode
from apps.accounts.services import user_has_role

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
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"


def can_manage_instruments(user):
    return bool(
        user
        and user.is_authenticated
        and (user.is_superuser or user_has_role(user, RoleCode.ADMIN, RoleCode.PI, RoleCode.INSTRUMENT_MANAGER))
    )


class InstrumentViewSet(viewsets.ModelViewSet):
    queryset = Instrument.objects.select_related("category", "manager", "manager__profile").prefetch_related("training_records")
    serializer_class = InstrumentSerializer
    permission_classes = [IsAuthenticated]
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


class InstrumentTrainingRecordViewSet(viewsets.ModelViewSet):
    queryset = InstrumentTrainingRecord.objects.select_related("instrument", "user", "user__profile", "trainer")
    serializer_class = InstrumentTrainingRecordSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(trainer=self.request.user)


class InstrumentMaintenanceRecordViewSet(viewsets.ModelViewSet):
    queryset = InstrumentMaintenanceRecord.objects.select_related("instrument", "maintainer")
    serializer_class = InstrumentMaintenanceRecordSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(maintainer=self.request.user)


class InstrumentFaultReportViewSet(viewsets.ModelViewSet):
    serializer_class = InstrumentFaultReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return InstrumentFaultReport.objects.select_related("instrument", "reporter", "handled_by")

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)
