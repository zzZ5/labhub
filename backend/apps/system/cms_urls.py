from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .cms_views import (
    CmsMemberViewSet,
    CmsAwardViewSet,
    CmsInstrumentCategoryViewSet,
    CmsInstrumentViewSet,
    CmsNewsArticleViewSet,
    CmsNewsCategoryViewSet,
    CmsNewsImageViewSet,
    CmsPatentViewSet,
    CmsPublicationViewSet,
    CmsProjectViewSet,
    CmsResearchDirectionViewSet,
    CmsContactInfoViewSet,
    CmsHomeBannerViewSet,
    CmsSiteSettingViewSet,
    CmsPortalContentImageViewSet,
)

router = DefaultRouter()
router.register("site-settings", CmsSiteSettingViewSet, basename="cms-site-setting")
router.register("content-images", CmsPortalContentImageViewSet, basename="cms-content-image")
router.register("contact-info", CmsContactInfoViewSet, basename="cms-contact-info")
router.register("home-banners", CmsHomeBannerViewSet, basename="cms-home-banner")
router.register("research-directions", CmsResearchDirectionViewSet, basename="cms-research-direction")
router.register("members", CmsMemberViewSet, basename="cms-member")
router.register("news-categories", CmsNewsCategoryViewSet, basename="cms-news-category")
router.register("news-articles", CmsNewsArticleViewSet, basename="cms-news-article")
router.register("news-images", CmsNewsImageViewSet, basename="cms-news-image")
router.register("publications", CmsPublicationViewSet, basename="cms-publication")
router.register("projects", CmsProjectViewSet, basename="cms-project")
router.register("patents", CmsPatentViewSet, basename="cms-patent")
router.register("awards", CmsAwardViewSet, basename="cms-award")
router.register("instrument-categories", CmsInstrumentCategoryViewSet, basename="cms-instrument-category")
router.register("instruments", CmsInstrumentViewSet, basename="cms-instrument")

urlpatterns = [
    path("", include(router.urls)),
]
