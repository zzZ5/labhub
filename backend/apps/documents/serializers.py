import mimetypes

from django.utils import timezone
from rest_framework import serializers

from apps.students.preview import refresh_file_preview_pdf
from apps.system.uploads import validate_upload_size

from .models import Document, DocumentCategory, DocumentDownloadLog, DocumentTag
from .services import can_delete_document, can_download_document, can_edit_document, can_view_document


class DocumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCategory
        fields = ["id", "name", "parent", "slug", "description", "sort_order"]


class DocumentTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTag
        fields = ["id", "name", "slug"]


class DocumentSerializer(serializers.ModelSerializer):
    category = DocumentCategorySerializer(read_only=True)
    tags = DocumentTagSerializer(many=True, read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    uploaded_by_name = serializers.CharField(source="uploaded_by.profile.real_name", read_only=True)
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
            "allow_download",
            "status",
            "status_label",
            "created_at",
            "updated_at",
            "original_filename",
            "uploaded_by_name",
            "uploaded_at",
            "file_size",
            "file_type",
            "preview_status",
            "preview_error",
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
        return bool(obj.file and self.get_can_view(obj))

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

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "category_id",
            "description",
            "allow_download",
            "status",
            "file",
        ]

    def validate_file(self, file_obj):
        return validate_upload_size(file_obj)

    def _replace_file(self, document, file_obj):
        if not file_obj:
            return document
        old_file = document.file.name if document.file else ""
        old_preview = document.preview_pdf.name if document.preview_pdf else ""
        document.file = file_obj
        document.original_filename = file_obj.name
        document.file_size = file_obj.size
        document.file_type = getattr(file_obj, "content_type", "") or mimetypes.guess_type(file_obj.name)[0] or ""
        document.uploaded_by = self.context["request"].user
        document.uploaded_at = timezone.now()
        document.preview_pdf = ""
        document.preview_status = "none"
        document.preview_error = ""
        document.save()
        if old_file and old_file != document.file.name:
            document.file.storage.delete(old_file)
        if old_preview:
            document.preview_pdf.storage.delete(old_preview)
        refresh_file_preview_pdf(document)
        return document

    def create(self, validated_data):
        file_obj = validated_data.pop("file", None)
        user = self.context["request"].user
        document = Document.objects.create(
            owner=user,
            uploaded_by=user,
            **validated_data,
        )
        return self._replace_file(document, file_obj)

    def update(self, instance, validated_data):
        file_obj = validated_data.pop("file", None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return self._replace_file(instance, file_obj)


class DocumentDownloadLogSerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source="document.title", read_only=True)

    class Meta:
        model = DocumentDownloadLog
        fields = ["id", "document", "document_title", "ip_address", "user_agent", "downloaded_at"]
