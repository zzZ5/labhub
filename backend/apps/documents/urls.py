from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DocumentCategoryViewSet, DocumentDownloadLogViewSet, DocumentTagViewSet, DocumentViewSet

router = DefaultRouter()
router.register("categories", DocumentCategoryViewSet, basename="document-category")
router.register("tags", DocumentTagViewSet, basename="document-tag")
router.register("documents", DocumentViewSet, basename="document")
router.register("download-logs", DocumentDownloadLogViewSet, basename="document-download-log")

urlpatterns = [
    path("", include(router.urls)),
]
