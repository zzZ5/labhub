from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    InstrumentCategoryViewSet,
    InstrumentFaultReportViewSet,
    InstrumentMaintenanceRecordViewSet,
    InstrumentTrainingRecordViewSet,
    InstrumentViewSet,
)

router = DefaultRouter()
router.register("categories", InstrumentCategoryViewSet, basename="instrument-category")
router.register("instruments", InstrumentViewSet, basename="instrument")
router.register("training-records", InstrumentTrainingRecordViewSet, basename="instrument-training-record")
router.register("maintenance-records", InstrumentMaintenanceRecordViewSet, basename="instrument-maintenance-record")
router.register("fault-reports", InstrumentFaultReportViewSet, basename="instrument-fault-report")

urlpatterns = [
    path("", include(router.urls)),
]
