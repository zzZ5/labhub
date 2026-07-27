from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ManageWechatAccountViewSet,
    ManageWechatArticleViewSet,
    PublicWechatAccountViewSet,
    PublicWechatArticleViewSet,
)

public_router = DefaultRouter()
public_router.register("accounts", PublicWechatAccountViewSet, basename="wechat-account")
public_router.register("articles", PublicWechatArticleViewSet, basename="wechat-article")

manage_router = DefaultRouter()
manage_router.register("accounts", ManageWechatAccountViewSet, basename="manage-wechat-account")
manage_router.register("articles", ManageWechatArticleViewSet, basename="manage-wechat-article")

urlpatterns = [
    path("", include(public_router.urls)),
    path("manage/", include(manage_router.urls)),
]

