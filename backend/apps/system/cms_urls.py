from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .cms_views import (
    CmsMemberViewSet,
    CmsInstrumentCategoryViewSet,
    CmsInstrumentViewSet,
    CmsNewsArticleViewSet,
    CmsNewsCategoryViewSet,
    CmsPublicationViewSet,
    CmsResearchDirectionViewSet,
)

router = DefaultRouter()
router.register("research-directions", CmsResearchDirectionViewSet, basename="cms-research-direction")
router.register("members", CmsMemberViewSet, basename="cms-member")
router.register("news-categories", CmsNewsCategoryViewSet, basename="cms-news-category")
router.register("news-articles", CmsNewsArticleViewSet, basename="cms-news-article")
router.register("publications", CmsPublicationViewSet, basename="cms-publication")
router.register("instrument-categories", CmsInstrumentCategoryViewSet, basename="cms-instrument-category")
router.register("instruments", CmsInstrumentViewSet, basename="cms-instrument")

urlpatterns = [
    path("", include(router.urls)),
]
