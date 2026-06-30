from rest_framework import serializers

from .models import ContactInfo, HomeBanner, ResearchDirection, SiteSetting


class SiteSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSetting
        fields = "__all__"


class ResearchDirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchDirection
        fields = ["id", "title", "slug", "summary", "content", "cover_image", "sort_order", "updated_at"]


class HomeBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeBanner
        fields = ["id", "title", "subtitle", "image", "link", "sort_order"]


class ContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInfo
        fields = "__all__"
