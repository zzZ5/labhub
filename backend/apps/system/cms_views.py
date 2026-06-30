from rest_framework import serializers, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from apps.accounts.permissions import CanManagePortalContent
from apps.instruments.models import Instrument, InstrumentCategory
from apps.instruments.serializers import InstrumentCategorySerializer
from apps.members.models import Member
from apps.members.serializers import MemberSerializer
from apps.news.models import NewsArticle, NewsCategory
from apps.news.serializers import NewsCategorySerializer
from apps.portal.models import ResearchDirection
from apps.portal.serializers import ResearchDirectionSerializer
from apps.publications.models import Publication
from apps.publications.serializers import PublicationSerializer


class CmsParserMixin:
    parser_classes = [JSONParser, FormParser, MultiPartParser]


class CmsResearchDirectionViewSet(CmsParserMixin, viewsets.ModelViewSet):
    queryset = ResearchDirection.objects.all()
    serializer_class = ResearchDirectionSerializer
    permission_classes = [CanManagePortalContent]
    lookup_field = "slug"


class CmsMemberViewSet(CmsParserMixin, viewsets.ModelViewSet):
    queryset = Member.objects.all().prefetch_related("educations", "experiences")
    serializer_class = MemberSerializer
    permission_classes = [CanManagePortalContent]


class CmsNewsCategoryViewSet(CmsParserMixin, viewsets.ModelViewSet):
    queryset = NewsCategory.objects.all()
    serializer_class = NewsCategorySerializer
    permission_classes = [CanManagePortalContent]
    lookup_field = "slug"


class CmsNewsArticleSerializer(serializers.ModelSerializer):
    category = NewsCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=NewsCategory.objects.all(),
        source="category",
        required=False,
        allow_null=True,
        write_only=True,
    )

    class Meta:
        model = NewsArticle
        fields = [
            "id",
            "title",
            "slug",
            "summary",
            "content",
            "cover_image",
            "category",
            "category_id",
            "event_date",
            "location",
            "visibility",
            "is_pinned",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class CmsNewsArticleViewSet(CmsParserMixin, viewsets.ModelViewSet):
    queryset = NewsArticle.objects.select_related("category", "author").all()
    serializer_class = CmsNewsArticleSerializer
    permission_classes = [CanManagePortalContent]
    lookup_field = "slug"


class CmsPublicationViewSet(CmsParserMixin, viewsets.ModelViewSet):
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    permission_classes = [CanManagePortalContent]


class CmsInstrumentSerializer(serializers.ModelSerializer):
    category = InstrumentCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=InstrumentCategory.objects.all(),
        source="category",
        required=False,
        allow_null=True,
        write_only=True,
    )
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Instrument
        fields = [
            "id",
            "name",
            "model",
            "serial_number",
            "category",
            "category_id",
            "room",
            "location_detail",
            "image",
            "status",
            "status_label",
            "need_training",
            "notes",
            "sort_order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status_label", "created_at", "updated_at"]


class CmsInstrumentCategoryViewSet(CmsParserMixin, viewsets.ModelViewSet):
    queryset = InstrumentCategory.objects.all()
    serializer_class = InstrumentCategorySerializer
    permission_classes = [CanManagePortalContent]
    lookup_field = "slug"


class CmsInstrumentViewSet(CmsParserMixin, viewsets.ModelViewSet):
    queryset = Instrument.objects.select_related("category").all()
    serializer_class = CmsInstrumentSerializer
    permission_classes = [CanManagePortalContent]
