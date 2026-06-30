from rest_framework.decorators import api_view, permission_classes
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


class PublicationViewSet(PublicVisibilityMixin, ReadOnlyModelViewSet):
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    filterset_fields = ["year", "is_representative"]


class ProjectViewSet(PublicVisibilityMixin, ReadOnlyModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class PatentViewSet(PublicVisibilityMixin, ReadOnlyModelViewSet):
    queryset = Patent.objects.all()
    serializer_class = PatentSerializer


class SoftwareCopyrightViewSet(PublicVisibilityMixin, ReadOnlyModelViewSet):
    queryset = SoftwareCopyright.objects.all()
    serializer_class = SoftwareCopyrightSerializer


class AwardViewSet(PublicVisibilityMixin, ReadOnlyModelViewSet):
    queryset = Award.objects.all()
    serializer_class = AwardSerializer


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
