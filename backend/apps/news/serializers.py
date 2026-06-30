from rest_framework import serializers

from .models import NewsArticle, NewsCategory, NewsImage, NewsTag


class NewsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsCategory
        fields = ["id", "name", "slug", "description", "sort_order"]


class NewsTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsTag
        fields = ["id", "name", "slug"]


class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImage
        fields = ["id", "image", "caption", "sort_order"]


class NewsArticleSerializer(serializers.ModelSerializer):
    category = NewsCategorySerializer(read_only=True)
    tags = NewsTagSerializer(many=True, read_only=True)
    images = NewsImageSerializer(many=True, read_only=True)

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
            "tags",
            "images",
            "event_date",
            "location",
            "is_pinned",
            "created_at",
            "updated_at",
        ]
