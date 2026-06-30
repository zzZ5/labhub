from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import NewsArticle, NewsCategory, Visibility
from .serializers import NewsArticleSerializer, NewsCategorySerializer


class NewsCategoryViewSet(ReadOnlyModelViewSet):
    queryset = NewsCategory.objects.all()
    serializer_class = NewsCategorySerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"


class NewsArticleViewSet(ReadOnlyModelViewSet):
    serializer_class = NewsArticleSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["category__slug"]
    search_fields = ["title", "summary", "content"]

    def get_queryset(self):
        return (
            NewsArticle.objects.filter(visibility=Visibility.PUBLIC, status=NewsArticle.Status.PUBLISHED)
            .select_related("category", "author")
            .prefetch_related("tags", "images")
        )
