from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.accounts.permissions import CanManagePortalContent

from .models import WechatAccount, WechatArticle
from .serializers import (
    WechatAccountManageSerializer,
    WechatAccountPublicSerializer,
    WechatArticleManageSerializer,
    WechatArticleSerializer,
)
from .tasks import sync_all_wechat_accounts, sync_wechat_account_task


class WechatArticlePagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 48


class PublicWechatAccountViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WechatAccountPublicSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return WechatAccount.objects.filter(is_active=True)


class PublicWechatArticleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WechatArticleSerializer
    permission_classes = [AllowAny]
    pagination_class = WechatArticlePagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["account"]
    search_fields = ["title"]

    def get_queryset(self):
        return WechatArticle.objects.filter(is_visible=True, account__is_active=True).select_related("account")


class ManageWechatAccountViewSet(viewsets.ModelViewSet):
    serializer_class = WechatAccountManageSerializer
    permission_classes = [CanManagePortalContent]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "description", "source_url"]
    ordering_fields = ["name", "sort_order", "created_at", "last_sync_success_at"]
    ordering = ["sort_order", "name"]

    def get_queryset(self):
        return WechatAccount.objects.annotate(article_count=Count("articles"))

    @action(detail=True, methods=["post"])
    def sync(self, request, pk=None):
        account = self.get_object()
        if account.source_type == WechatAccount.SourceType.MANUAL:
            return Response({"detail": "该公众号设置为仅手动录入，无需同步。"}, status=status.HTTP_400_BAD_REQUEST)
        sync_wechat_account_task.delay(account.pk)
        return Response({"detail": "同步任务已提交，请稍后刷新查看结果。"}, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=["post"], url_path="sync-all")
    def sync_all(self, request):
        sync_all_wechat_accounts.delay()
        return Response({"detail": "全部公众号同步任务已提交，请稍后刷新查看结果。"}, status=status.HTTP_202_ACCEPTED)


class ManageWechatArticleViewSet(viewsets.ModelViewSet):
    serializer_class = WechatArticleManageSerializer
    permission_classes = [CanManagePortalContent]
    pagination_class = WechatArticlePagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["account", "is_visible", "is_manual"]
    search_fields = ["title", "summary"]
    ordering_fields = ["published_at", "created_at", "title"]
    ordering = ["-published_at", "-id"]

    def get_queryset(self):
        return WechatArticle.objects.select_related("account")
