from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .paper_views import ManageOriginalPaperViewSet, PublicOriginalPaperViewSet

from .views import (
    ManageWechatAccountViewSet,
    ManageWechatArticleViewSet,
    PublicWechatAccountViewSet,
    PublicWechatArticleViewSet,
)

public_router = DefaultRouter()
public_router.register("accounts", PublicWechatAccountViewSet, basename="wechat-account")
public_router.register("articles", PublicWechatArticleViewSet, basename="wechat-article")
public_router.register("papers", PublicOriginalPaperViewSet, basename="original-paper")

manage_router = DefaultRouter()
manage_router.register("accounts", ManageWechatAccountViewSet, basename="manage-wechat-account")
manage_router.register("articles", ManageWechatArticleViewSet, basename="manage-wechat-article")
manage_router.register("papers", ManageOriginalPaperViewSet, basename="manage-original-paper")

urlpatterns = [
    path("", include(public_router.urls)),
    path("manage/", include(manage_router.urls)),
]

