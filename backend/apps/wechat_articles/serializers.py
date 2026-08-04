from rest_framework import serializers

from .models import WechatAccount, WechatArticle, article_dedupe_key, is_wechat_article_url


class WechatAccountPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = WechatAccount
        fields = ["id", "name", "description"]


class WechatAccountManageSerializer(serializers.ModelSerializer):
    source_type_label = serializers.CharField(source="get_source_type_display", read_only=True)
    article_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = WechatAccount
        fields = [
            "id",
            "name",
            "description",
            "source_type",
            "source_type_label",
            "source_url",
            "api_token_env",
            "is_active",
            "sort_order",
            "article_count",
            "last_sync_attempt_at",
            "last_sync_success_at",
            "last_sync_error",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "article_count",
            "last_sync_attempt_at",
            "last_sync_success_at",
            "last_sync_error",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        source_type = attrs.get("source_type", getattr(self.instance, "source_type", WechatAccount.SourceType.MANUAL))
        source_url = attrs.get("source_url", getattr(self.instance, "source_url", ""))
        if source_type != WechatAccount.SourceType.MANUAL and not source_url:
            raise serializers.ValidationError({"source_url": "RSS 或开放接口同步必须填写来源地址。"})
        return attrs


class WechatArticleSerializer(serializers.ModelSerializer):
    account = WechatAccountPublicSerializer(read_only=True)
    source_url = serializers.SerializerMethodField()

    def get_source_url(self, obj):
        if is_wechat_article_url(obj.source_guid):
            return obj.source_guid.strip()
        return obj.source_url

    class Meta:
        model = WechatArticle
        fields = [
            "id",
            "account",
            "title",
            "summary",
            "cover_url",
            "source_url",
            "published_at",
            "created_at",
            "updated_at",
        ]


class WechatArticleManageSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source="account.name", read_only=True)

    class Meta:
        model = WechatArticle
        fields = [
            "id",
            "account",
            "account_name",
            "title",
            "summary",
            "cover_url",
            "source_url",
            "source_guid",
            "published_at",
            "is_visible",
            "is_manual",
            "synced_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["is_manual", "synced_at", "created_at", "updated_at"]

    def validate(self, attrs):
        account = attrs.get("account", getattr(self.instance, "account", None))
        title = attrs.get("title", getattr(self.instance, "title", ""))
        source_url = attrs.get("source_url", getattr(self.instance, "source_url", ""))
        source_guid = attrs.get("source_guid", getattr(self.instance, "source_guid", "") if self.instance else "")
        published_at = attrs.get("published_at", getattr(self.instance, "published_at", None))
        if account:
            key = article_dedupe_key(
                account.pk,
                source_guid=source_guid,
                source_url=source_url,
                title=title,
                published_at=published_at,
            )
            queryset = WechatArticle.objects.filter(dedupe_key=key)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError({"source_url": "该公众号下已存在同一篇文章。"})
        return attrs

    def create(self, validated_data):
        validated_data["is_manual"] = True
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["created_by"] = request.user
        return super().create(validated_data)
