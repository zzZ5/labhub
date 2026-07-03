from uuid import uuid4

from django.utils.text import slugify
from rest_framework import serializers, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from apps.accounts.permissions import CanManagePortalContent
from apps.instruments.models import Instrument, InstrumentCategory
from apps.instruments.serializers import InstrumentCategorySerializer
from apps.members.models import Member
from apps.members.serializers import MemberSerializer
from apps.news.models import NewsArticle, NewsCategory, NewsImage
from apps.news.serializers import NewsCategorySerializer, NewsImageSerializer
from apps.system.uploads import validate_upload_size
from apps.portal.models import ContactInfo, ResearchDirection, SiteSetting
from apps.portal.serializers import ContactInfoSerializer, ResearchDirectionSerializer, SiteSettingSerializer
from apps.publications.models import Award, Patent, Project, Publication
from apps.publications.serializers import AwardSerializer, PatentSerializer, ProjectSerializer, PublicationSerializer


class CmsParserMixin:
    parser_classes = [JSONParser, FormParser, MultiPartParser]


def unique_slug(model, title, current_slug="", prefix="item"):
    base = slugify(title or "", allow_unicode=False)[:90].strip("-") or f"{prefix}-{uuid4().hex[:8]}"
    slug = base
    index = 2
    queryset = model.objects.all()
    if current_slug:
        queryset = queryset.exclude(slug=current_slug)
    while queryset.filter(slug=slug).exists():
        suffix = f"-{index}"
        slug = f"{base[: 120 - len(suffix)]}{suffix}"
        index += 1
    return slug


class CmsResearchDirectionSerializer(ResearchDirectionSerializer):
    slug = serializers.SlugField(required=False, allow_blank=True)

    def create(self, validated_data):
        validated_data["slug"] = unique_slug(ResearchDirection, validated_data.get("title"), prefix="research")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if not instance.slug:
            validated_data["slug"] = unique_slug(ResearchDirection, validated_data.get("title") or instance.title, instance.slug, prefix="research")
        else:
            validated_data.pop("slug", None)
        return super().update(instance, validated_data)


class CmsResearchDirectionViewSet(CmsParserMixin, viewsets.ModelViewSet):
    queryset = ResearchDirection.objects.all()
    serializer_class = CmsResearchDirectionSerializer
    permission_classes = [CanManagePortalContent]
    lookup_field = "slug"


class CmsSiteSettingViewSet(CmsParserMixin, viewsets.ModelViewSet):
    queryset = SiteSetting.objects.all().order_by("-updated_at")
    serializer_class = SiteSettingSerializer
    permission_classes = [CanManagePortalContent]


class CmsContactInfoViewSet(CmsParserMixin, viewsets.ModelViewSet):
    queryset = ContactInfo.objects.all().order_by("-updated_at")
    serializer_class = ContactInfoSerializer
    permission_classes = [CanManagePortalContent]


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
    images = NewsImageSerializer(many=True, read_only=True)
    slug = serializers.SlugField(required=False, allow_blank=True)
    content = serializers.CharField(required=False, allow_blank=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=NewsCategory.objects.all(),
        source="category",
        required=False,
        allow_null=True,
        write_only=True,
    )
    word_file = serializers.FileField(required=False)

    class Meta:
        model = NewsArticle
        fields = [
            "id",
            "title",
            "slug",
            "summary",
            "content",
            "cover_image",
            "word_file",
            "category",
            "category_id",
            "images",
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
        validated_data["slug"] = unique_slug(NewsArticle, validated_data.get("title"), prefix="news")
        self._validate_word_file(validated_data)
        validated_data.setdefault("content", "")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("slug", None)
        self._validate_word_file(validated_data)
        return super().update(instance, validated_data)

    def _validate_word_file(self, validated_data):
        word_file = validated_data.get("word_file")
        if not word_file:
            return
        validate_upload_size(word_file)
        filename = getattr(word_file, "name", "")
        if not filename.lower().endswith(".docx"):
            raise serializers.ValidationError({"word_file": "请上传 .docx 格式的 Word 文档。"})


class CmsNewsArticleViewSet(CmsParserMixin, viewsets.ModelViewSet):
    queryset = NewsArticle.objects.select_related("category", "author").prefetch_related("images").all()
    serializer_class = CmsNewsArticleSerializer
    permission_classes = [CanManagePortalContent]
    lookup_field = "slug"


class CmsNewsImageSerializer(serializers.ModelSerializer):
    article_id = serializers.PrimaryKeyRelatedField(queryset=NewsArticle.objects.all(), source="article", write_only=True)

    class Meta:
        model = NewsImage
        fields = ["id", "article", "article_id", "image", "caption", "sort_order"]
        read_only_fields = ["id", "article"]

    def validate_image(self, image):
        return validate_upload_size(image)


class CmsNewsImageViewSet(CmsParserMixin, viewsets.ModelViewSet):
    queryset = NewsImage.objects.select_related("article").all()
    serializer_class = CmsNewsImageSerializer
    permission_classes = [CanManagePortalContent]


class CmsPublicationViewSet(CmsParserMixin, viewsets.ModelViewSet):
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    permission_classes = [CanManagePortalContent]


class CmsProjectViewSet(CmsParserMixin, viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [CanManagePortalContent]


class CmsPatentViewSet(CmsParserMixin, viewsets.ModelViewSet):
    queryset = Patent.objects.all()
    serializer_class = PatentSerializer
    permission_classes = [CanManagePortalContent]


class CmsAwardViewSet(CmsParserMixin, viewsets.ModelViewSet):
    queryset = Award.objects.all()
    serializer_class = AwardSerializer
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
