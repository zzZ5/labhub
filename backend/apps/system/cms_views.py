import logging
from uuid import uuid4

from django.core.files.base import ContentFile
from django.conf import settings
from django.utils.text import slugify
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from apps.accounts.permissions import CanManagePortalContent
from apps.instruments.models import Instrument, InstrumentCategory
from apps.instruments.serializers import InstrumentCategorySerializer
from apps.members.models import Member
from apps.members.serializers import MemberSerializer
from apps.news.models import NewsArticle, NewsCategory, NewsImage
from apps.news.serializers import (
    NewsCategorySerializer,
    NewsImageSerializer,
    extract_docx_images,
    parse_docx_blocks,
    render_docx_blocks,
    sanitize_news_html,
)
from apps.system.uploads import validate_upload_size
from apps.portal.models import ContactInfo, HomeBanner, ResearchDirection, SiteSetting
from apps.portal.serializers import ContactInfoSerializer, HomeBannerSerializer, ResearchDirectionSerializer, SiteSettingSerializer
from apps.publications.models import Award, Patent, Project, Publication
from apps.publications.serializers import AwardSerializer, PatentSerializer, ProjectSerializer, PublicationSerializer

from .cms_importers import import_rows, parse_publication_citation

logger = logging.getLogger(__name__)


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


class CmsHomeBannerViewSet(CmsParserMixin, viewsets.ModelViewSet):
    queryset = HomeBanner.objects.all()
    serializer_class = HomeBannerSerializer
    permission_classes = [CanManagePortalContent]


class CmsMemberViewSet(CmsParserMixin, viewsets.ModelViewSet):
    queryset = Member.objects.all().prefetch_related("educations", "experiences")
    serializer_class = MemberSerializer
    permission_classes = [CanManagePortalContent]

    @action(detail=False, methods=["post"], url_path="import-file")
    def import_file(self, request):
        upload = request.FILES.get("file")
        if not upload:
            return Response({"detail": "请上传团队成员导入文件。"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            result = import_rows(upload, upload.name, "members")
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            logger.exception("Member import failed")
            detail = f"导入失败：{exc}" if settings.DEBUG else "导入失败，请检查模板列名和日期格式。"
            return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)


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
            "word_html",
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
        read_only_fields = ["id", "word_html", "created_at", "updated_at"]

    def validate_content(self, value):
        return sanitize_news_html(value)

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        validated_data["slug"] = unique_slug(NewsArticle, validated_data.get("title"), prefix="news")
        self._validate_word_file(validated_data)
        validated_data.setdefault("content", "")
        article = super().create(validated_data)
        if article.word_file:
            self._sync_word_images(article)
        return article

    def update(self, instance, validated_data):
        validated_data.pop("slug", None)
        has_new_word_file = "word_file" in validated_data
        has_new_content = "content" in validated_data
        self._validate_word_file(validated_data)
        article = super().update(instance, validated_data)
        if has_new_word_file and article.word_file:
            self._sync_word_images(article)
        elif has_new_content and article.word_html:
            article.word_html = ""
            article.save(update_fields=["word_html", "updated_at"])
        return article

    def _validate_word_file(self, validated_data):
        word_file = validated_data.get("word_file")
        if not word_file:
            return
        validate_upload_size(word_file)
        filename = getattr(word_file, "name", "")
        if not filename.lower().endswith(".docx"):
            raise serializers.ValidationError({"word_file": "请上传 .docx 格式的 Word 文档。"})

    def _sync_word_images(self, article):
        NewsImage.objects.filter(article=article, caption__startswith="Word ").delete()
        try:
            with article.word_file.open("rb") as file_obj:
                blocks = parse_docx_blocks(file_obj)
            with article.word_file.open("rb") as file_obj:
                images = extract_docx_images(file_obj)
        except Exception:
            article.word_html = ""
            article.save(update_fields=["word_html", "updated_at"])
            return

        first_image_file = None
        image_urls = {}
        for index, (image_path, filename, image_data) in enumerate(images[:20], start=1):
            image_file = ContentFile(image_data, name=filename)
            news_image = NewsImage.objects.create(
                article=article,
                image=image_file,
                caption=f"Word 图片 {index}",
                sort_order=index,
            )
            image_urls[image_path] = news_image.image.url
            if first_image_file is None:
                first_image_file = ContentFile(image_data, name=filename)

        article.word_html = sanitize_news_html(render_docx_blocks(blocks, image_urls))
        article.content = article.word_html
        article.save(update_fields=["word_html", "content", "updated_at"])

        if first_image_file and not article.cover_image:
            article.cover_image.save(first_image_file.name, first_image_file, save=True)


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

    @action(detail=False, methods=["post"], url_path="parse-citation")
    def parse_citation(self, request):
        citation = str(request.data.get("citation", "")).strip()
        if not citation:
            return Response({"detail": "请填写论文引文。"}, status=status.HTTP_400_BAD_REQUEST)
        parsed = parse_publication_citation(citation)
        missing = [field for field in ("authors", "title", "journal", "year") if not parsed.get(field)]
        return Response({**parsed, "complete": not missing, "missing_fields": missing})

    @action(detail=False, methods=["post"], url_path="import-file")
    def import_file(self, request):
        return import_cms_file(request, "publications", "请上传论文成果导入文件。")


class CmsProjectViewSet(CmsParserMixin, viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [CanManagePortalContent]

    @action(detail=False, methods=["post"], url_path="import-file")
    def import_file(self, request):
        return import_cms_file(request, "projects", "请上传科研项目导入文件。")


class CmsPatentViewSet(CmsParserMixin, viewsets.ModelViewSet):
    queryset = Patent.objects.all()
    serializer_class = PatentSerializer
    permission_classes = [CanManagePortalContent]

    @action(detail=False, methods=["post"], url_path="import-file")
    def import_file(self, request):
        return import_cms_file(request, "patents", "请上传专利成果导入文件。")


class CmsAwardViewSet(CmsParserMixin, viewsets.ModelViewSet):
    queryset = Award.objects.all()
    serializer_class = AwardSerializer
    permission_classes = [CanManagePortalContent]

    @action(detail=False, methods=["post"], url_path="import-file")
    def import_file(self, request):
        return import_cms_file(request, "awards", "请上传获奖成果导入文件。")


def import_cms_file(request, kind: str, missing_message: str):
    upload = request.FILES.get("file")
    if not upload:
        return Response({"detail": missing_message}, status=status.HTTP_400_BAD_REQUEST)
    try:
        result = import_rows(upload, upload.name, kind)
    except ValueError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as exc:
        logger.exception("CMS import failed: %s", kind)
        detail = f"导入失败：{exc}" if settings.DEBUG else "导入失败，请检查模板列名、日期格式和必填字段。"
        return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)
    return Response(result)


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
            "category",
            "category_id",
            "location_detail",
            "manager",
            "image",
            "status",
            "status_label",
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
