from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import InstrumentCategoryViewSet, InstrumentViewSet

router = DefaultRouter()
router.register("categories", InstrumentCategoryViewSet, basename="instrument-category")
router.register("instruments", InstrumentViewSet, basename="instrument")

urlpatterns = [
    path("", include(router.urls)),
]
