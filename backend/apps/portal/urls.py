from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import HomeBannerViewSet, ResearchDirectionViewSet, contact_info, site_setting

router = DefaultRouter()
router.register("research-directions", ResearchDirectionViewSet, basename="public-research-direction")
router.register("banners", HomeBannerViewSet, basename="public-home-banner")

urlpatterns = [
    path("site-setting/", site_setting, name="public-site-setting"),
    path("contact/", contact_info, name="public-contact"),
    path("", include(router.urls)),
]
