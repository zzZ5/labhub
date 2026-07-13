from rest_framework import serializers

from apps.system.serializer_fields import file_field_size

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


class ResearchDirectionSerializer(serializers.ModelSerializer):
    cover_image_size = serializers.SerializerMethodField()

    class Meta:
        model = ResearchDirection
        fields = ["id", "title", "slug", "summary", "content", "cover_image", "cover_image_size", "sort_order", "updated_at"]

    def get_cover_image_size(self, obj):
        return file_field_size(obj.cover_image)


class HomeBannerSerializer(serializers.ModelSerializer):
    image_size = serializers.SerializerMethodField()

    class Meta:
        model = HomeBanner
        fields = ["id", "title", "subtitle", "image", "image_size", "link", "sort_order", "is_active"]

    def get_image_size(self, obj):
        return file_field_size(obj.image)


class ContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInfo
        fields = "__all__"
