from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NewsArticleViewSet, NewsCategoryViewSet

router = DefaultRouter()
router.register("categories", NewsCategoryViewSet, basename="public-news-category")
router.register("articles", NewsArticleViewSet, basename="public-news-article")

urlpatterns = [
    path("", include(router.urls)),
]
