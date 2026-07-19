from rest_framework import serializers

from apps.system.serializer_fields import file_field_size
from apps.system.rich_text import sanitize_rich_text_html
from apps.system.uploads import validate_favicon_upload, validate_image_upload, validate_logo_upload

from .models import ContactInfo, HomeBanner, ResearchDirection, SiteSetting


class SiteSettingSerializer(serializers.ModelSerializer):
    logo_size = serializers.SerializerMethodField()
    favicon_size = serializers.SerializerMethodField()
    hero_image_size = serializers.SerializerMethodField()

    class Meta:
        model = SiteSetting
        fields = "__all__"

    def get_logo_size(self, obj):
        return file_field_size(obj.logo)

    def get_favicon_size(self, obj):
        return file_field_size(obj.favicon)

    def get_hero_image_size(self, obj):
        return file_field_size(obj.hero_image)

    def validate_logo(self, value):
        return validate_logo_upload(value)

    def validate_favicon(self, value):
        return validate_favicon_upload(value)

    def validate_hero_image(self, value):
        return validate_image_upload(value)


class ResearchDirectionSerializer(serializers.ModelSerializer):
    cover_image_size = serializers.SerializerMethodField()

    class Meta:
        model = ResearchDirection
        fields = ["id", "title", "slug", "summary", "content", "cover_image", "cover_image_size", "sort_order", "view_count", "created_at", "updated_at"]

    def get_cover_image_size(self, obj):
        return file_field_size(obj.cover_image)

    def validate_cover_image(self, value):
        return validate_image_upload(value)

    def validate_content(self, value):
        return sanitize_rich_text_html(value)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["content"] = sanitize_rich_text_html(data.get("content"))
        return data


class HomeBannerSerializer(serializers.ModelSerializer):
    image_size = serializers.SerializerMethodField()

    class Meta:
        model = HomeBanner
        fields = ["id", "title", "subtitle", "image", "image_size", "link", "sort_order", "is_active"]

    def get_image_size(self, obj):
        return file_field_size(obj.image)

    def validate_image(self, value):
        return validate_image_upload(value)


class ContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInfo
        fields = "__all__"
