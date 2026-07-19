from rest_framework import filters
from django.db.models import F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.news.models import Visibility

from .models import Award, Book, Patent, Project, Publication, SoftwareCopyright, Standard
from .serializers import (
    AwardSerializer,
    BookSerializer,
    PatentSerializer,
    ProjectSerializer,
    PublicationSerializer,
    SoftwareCopyrightSerializer,
    StandardSerializer,
)


class PublicVisibilityMixin:
    permission_classes = [AllowAny]

    def get_queryset(self):
        return self.queryset.filter(visibility=Visibility.PUBLIC)


class PublicResultsPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 100


class PublicDetailTrackingMixin:
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        type(instance).objects.filter(pk=instance.pk).update(view_count=F("view_count") + 1)
        instance.refresh_from_db(fields=["view_count"])
        return Response(self.get_serializer(instance).data)


class PublicationViewSet(PublicDetailTrackingMixin, PublicVisibilityMixin, ReadOnlyModelViewSet):
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    pagination_class = PublicResultsPagination
    filterset_fields = ["year", "is_representative"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "authors", "journal", "doi", "abstract"]
    ordering_fields = ["year", "sort_order", "created_at"]
    ordering = ["-year", "-created_at"]


class ProjectViewSet(PublicDetailTrackingMixin, PublicVisibilityMixin, ReadOnlyModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    pagination_class = PublicResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "project_number", "funding_source", "principal_investigator", "status", "description"]
    ordering_fields = ["sort_order", "start_date", "end_date", "title"]
    ordering = ["-start_date", "-end_date", "title"]


class PatentViewSet(PublicDetailTrackingMixin, PublicVisibilityMixin, ReadOnlyModelViewSet):
    queryset = Patent.objects.all()
    serializer_class = PatentSerializer
    pagination_class = PublicResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "patent_number", "inventors", "status", "description"]
    ordering_fields = ["sort_order", "application_date", "authorization_date", "title"]
    ordering = ["-application_date", "-authorization_date", "title"]


class SoftwareCopyrightViewSet(PublicVisibilityMixin, ReadOnlyModelViewSet):
    queryset = SoftwareCopyright.objects.all()
    serializer_class = SoftwareCopyrightSerializer


class AwardViewSet(PublicDetailTrackingMixin, PublicVisibilityMixin, ReadOnlyModelViewSet):
    queryset = Award.objects.all()
    serializer_class = AwardSerializer
    pagination_class = PublicResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "award_level", "participants", "description"]
    ordering_fields = ["sort_order", "award_date", "title"]
    ordering = ["-award_date", "title"]


class StandardViewSet(PublicVisibilityMixin, ReadOnlyModelViewSet):
    queryset = Standard.objects.all()
    serializer_class = StandardSerializer


class BookViewSet(PublicVisibilityMixin, ReadOnlyModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def public_stats(request):
    return Response(
        {
            "publications": Publication.objects.filter(visibility=Visibility.PUBLIC).count(),
            "projects": Project.objects.filter(visibility=Visibility.PUBLIC).count(),
            "patents": Patent.objects.filter(visibility=Visibility.PUBLIC).count(),
            "awards": Award.objects.filter(visibility=Visibility.PUBLIC).count(),
        }
    )
