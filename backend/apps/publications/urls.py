from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AwardViewSet,
    BookViewSet,
    PatentViewSet,
    ProjectViewSet,
    PublicationViewSet,
    SoftwareCopyrightViewSet,
    StandardViewSet,
    public_stats,
)

router = DefaultRouter()
router.register("publications", PublicationViewSet, basename="public-publication")
router.register("projects", ProjectViewSet, basename="public-project")
router.register("patents", PatentViewSet, basename="public-patent")
router.register("software-copyrights", SoftwareCopyrightViewSet, basename="public-software-copyright")
router.register("awards", AwardViewSet, basename="public-award")
router.register("standards", StandardViewSet, basename="public-standard")
router.register("books", BookViewSet, basename="public-book")

urlpatterns = [
    path("stats/", public_stats, name="public-publication-stats"),
    path("", include(router.urls)),
]
