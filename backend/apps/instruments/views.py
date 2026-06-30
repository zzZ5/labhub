from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

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


class InstrumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Instrument.objects.select_related("category", "manager", "manager__profile").prefetch_related("training_records")
    serializer_class = InstrumentSerializer
    permission_classes = [IsAuthenticated]


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
