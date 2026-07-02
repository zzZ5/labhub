from rest_framework import serializers

from apps.students.preview import refresh_file_preview_pdf

from .models import Document, DocumentCategory, DocumentDownloadLog, DocumentTag, DocumentVersion
from .services import can_delete_document, can_download_document, can_edit_document, can_view_document


class DocumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCategory
        fields = ["id", "name", "parent", "slug", "description", "sort_order", "visibility"]


class DocumentTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTag
        fields = ["id", "name", "slug"]


class DocumentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentVersion
        fields = [
            "id",
            "version",
            "original_filename",
            "change_log",
            "uploaded_at",
            "file_size",
            "file_type",
            "is_current",
            "preview_status",
            "preview_error",
        ]


class DocumentSerializer(serializers.ModelSerializer):
    category = DocumentCategorySerializer(read_only=True)
    tags = DocumentTagSerializer(many=True, read_only=True)
    versions = DocumentVersionSerializer(many=True, read_only=True)
    visibility_label = serializers.CharField(source="get_visibility_display", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    can_view = serializers.SerializerMethodField()
    can_preview = serializers.SerializerMethodField()
    can_download = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "category",
            "tags",
            "description",
            "current_version",
            "visibility",
            "visibility_label",
            "allow_download",
            "status",
            "status_label",
            "created_at",
            "updated_at",
            "versions",
            "can_view",
            "can_preview",
            "can_download",
            "can_edit",
            "can_delete",
        ]

    def get_can_view(self, obj):
        request = self.context.get("request")
        return can_view_document(getattr(request, "user", None), obj)

    def get_can_download(self, obj):
        request = self.context.get("request")
        return can_download_document(getattr(request, "user", None), obj)

    def get_can_preview(self, obj):
        return bool(obj.current_file and self.get_can_view(obj))

    def get_can_edit(self, obj):
        request = self.context.get("request")
        return can_edit_document(getattr(request, "user", None), obj)

    def get_can_delete(self, obj):
        request = self.context.get("request")
        return can_delete_document(getattr(request, "user", None), obj)


class DocumentWriteSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=DocumentCategory.objects.all(),
        source="category",
        required=False,
        allow_null=True,
    )
    file = serializers.FileField(write_only=True, required=False)
    version = serializers.CharField(write_only=True, required=False, allow_blank=True)
    change_log = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "category_id",
            "description",
            "visibility",
            "allow_download",
            "status",
            "file",
            "version",
            "change_log",
        ]

    def _create_version(self, document, validated_data):
        file = validated_data.pop("file", None)
        version = validated_data.pop("version", "") or document.current_version or "v1.0"
        change_log = validated_data.pop("change_log", "")
        if file:
            version_obj = DocumentVersion.objects.create(
                document=document,
                version=version,
                file=file,
                change_log=change_log,
                uploaded_by=self.context["request"].user,
                is_current=True,
            )
            refresh_file_preview_pdf(version_obj)

    def create(self, validated_data):
        file_data = {
            "file": validated_data.pop("file", None),
            "version": validated_data.pop("version", "") or "v1.0",
            "change_log": validated_data.pop("change_log", ""),
        }
        document = Document.objects.create(
            owner=self.context["request"].user,
            maintainer=self.context["request"].user,
            current_version=file_data["version"],
            **validated_data,
        )
        self._create_version(document, file_data)
        return document

    def update(self, instance, validated_data):
        file_data = {
            "file": validated_data.pop("file", None),
            "version": validated_data.pop("version", "") or instance.current_version or "v1.0",
            "change_log": validated_data.pop("change_log", ""),
        }
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        self._create_version(instance, file_data)
        return instance


class DocumentDownloadLogSerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source="document.title", read_only=True)
    version_label = serializers.CharField(source="version.version", read_only=True)

    class Meta:
        model = DocumentDownloadLog
        fields = ["id", "document", "document_title", "version", "version_label", "ip_address", "user_agent", "downloaded_at"]
