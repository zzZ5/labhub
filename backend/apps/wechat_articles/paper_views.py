from django.http import Http404
from django.db.models import F
from django.db.models.functions import Lower
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.throttling import UserRateThrottle
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from apps.accounts.permissions import CanManagePortalContent
from apps.documents.responses import protected_file_response

from .models import OriginalPaper
from .paper_serializers import OriginalPaperManageSerializer, OriginalPaperSerializer
from .views import WechatArticlePagination
from .paper_metadata import MetadataError, fetch_paper_metadata


class MetadataLookupThrottle(UserRateThrottle):
    rate = "30/min"


class PublicOriginalPaperViewSet(ReadOnlyModelViewSet):
    queryset = OriginalPaper.objects.filter(is_visible=True)
    serializer_class = OriginalPaperSerializer
    permission_classes = [AllowAny]
    pagination_class = WechatArticlePagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["topic"]
    search_fields = ["title", "chinese_title", "doi", "authors", "journal"]

    def get_queryset(self):
        # Year is the available publication precision; do not infer dates from DOI or upload time.
        ordering = self.request.query_params.get("sort", "added")
        choices = {
            "year_desc": [F("year").desc(nulls_last=True), Lower("title"), "id"],
            "year_asc": [F("year").asc(nulls_last=True), Lower("title"), "id"],
            "title": [Lower("title"), "id"],
            "added": ["-created_at", "-id"],
        }
        return super().get_queryset().order_by(*choices.get(ordering, choices["added"]))

    def pdf_response(self, attachment):
        paper = self.get_object()
        if not paper.can_share_pdf:
            raise Http404
        try:
            response = protected_file_response(
                paper.pdf, f"paper-{paper.pk}.pdf", as_attachment=attachment, content_type="application/pdf",
            )
        except (FileNotFoundError, OSError):
            raise Http404
        response["Cache-Control"] = "no-store"
        response["X-Content-Type-Options"] = "nosniff"
        return response

    @action(detail=True, methods=["get"])
    def preview(self, request, pk=None):
        return self.pdf_response(False)

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        return self.pdf_response(True)


class ManageOriginalPaperViewSet(ModelViewSet):
    queryset = OriginalPaper.objects.all()
    serializer_class = OriginalPaperManageSerializer
    permission_classes = [CanManagePortalContent]
    pagination_class = WechatArticlePagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["topic", "is_visible"]
    search_fields = PublicOriginalPaperViewSet.search_fields

    @action(detail=False, methods=["post"], throttle_classes=[MetadataLookupThrottle])
    def lookup(self, request):
        try:
            result = fetch_paper_metadata(request.data.get("doi"))
        except MetadataError as exc:
            raise serializers.ValidationError({"doi": str(exc)}) from exc
        return Response(result)
