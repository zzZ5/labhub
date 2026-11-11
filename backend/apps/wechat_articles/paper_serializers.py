from rest_framework import serializers
from rest_framework.reverse import reverse

from .models import OriginalPaper, is_wechat_article_url
from .paper_metadata import MetadataError, fetch_paper_metadata, normalize_doi


class OriginalPaperSerializer(serializers.ModelSerializer):
    topic_label = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    def get_topic_label(self, obj):
        return obj.get_topic_display() or "未分类"

    def file_url(self, obj, action):
        if not obj.can_share_pdf:
            return ""
        return reverse(f"original-paper-{action}", args=[obj.pk])

    def get_preview_url(self, obj):
        return self.file_url(obj, "preview")

    def get_download_url(self, obj):
        return self.file_url(obj, "download")

    class Meta:
        model = OriginalPaper
        fields = ["id", "title", "chinese_title", "authors", "journal", "year", "doi", "topic",
                  "topic_label", "publisher_url", "wechat_url", "preview_url", "download_url"]


class OriginalPaperManageSerializer(OriginalPaperSerializer):
    title = serializers.CharField(max_length=500, required=False, allow_blank=True)
    pdf = serializers.FileField(write_only=True, required=False)
    has_pdf = serializers.SerializerMethodField()
    remove_pdf = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta(OriginalPaperSerializer.Meta):
        fields = OriginalPaperSerializer.Meta.fields + [
            "pdf", "has_pdf", "remove_pdf", "sharing", "rights_note", "is_visible", "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_has_pdf(self, obj):
        return bool(obj.pdf)

    def validate_doi(self, value):
        try:
            value = normalize_doi(value)
        except MetadataError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        if not value:
            return None
        queryset = OriginalPaper.objects.filter(doi=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("该 DOI 已收录，请编辑已有条目。")
        return value

    def validate_wechat_url(self, value):
        if value and not is_wechat_article_url(value):
            raise serializers.ValidationError("请填写公众号正式文章链接。")
        return value

    def validate_pdf(self, value):
        if not value.name.lower().endswith(".pdf") or value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError("请上传不超过 50 MB 的 PDF。")
        position = value.tell()
        header = value.read(5)
        value.seek(position)
        if header != b"%PDF-":
            raise serializers.ValidationError("文件内容不是有效的 PDF 格式。")
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        sharing = attrs.get("sharing", getattr(self.instance, "sharing", OriginalPaper.Sharing.LINK_ONLY))
        note = attrs.get("rights_note", getattr(self.instance, "rights_note", ""))
        if sharing != OriginalPaper.Sharing.LINK_ONLY and not note.strip():
            raise serializers.ValidationError({"rights_note": "请填写允许分享的许可说明或授权依据。"})
        if attrs.get("remove_pdf") and attrs.get("pdf"):
            raise serializers.ValidationError({"pdf": "上传新文件和移除文件不能同时操作。"})
        if not attrs.get("title", getattr(self.instance, "title", "")):
            doi = attrs.get("doi", getattr(self.instance, "doi", None))
            try:
                metadata = fetch_paper_metadata(doi)
            except MetadataError as exc:
                raise serializers.ValidationError({"doi": str(exc)}) from exc
            for field in ["title", "authors", "journal", "year", "publisher_url", "topic"]:
                if not attrs.get(field):
                    attrs[field] = metadata[field]
        return attrs

    def create(self, validated_data):
        validated_data.pop("remove_pdf", None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.pop("remove_pdf", False):
            # Unlink the record; retain stored bytes until a separate cleanup.
            validated_data["pdf"] = ""
        return super().update(instance, validated_data)
