from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import StudentArchiveFileViewSet, StudentProfileViewSet

router = DefaultRouter()
router.register("profiles", StudentProfileViewSet, basename="student-profile")
router.register("archive-files", StudentArchiveFileViewSet, basename="student-archive-file")

urlpatterns = [
    path("", include(router.urls)),
]
