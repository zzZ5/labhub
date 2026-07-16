from rest_framework import serializers

from apps.system.serializer_fields import file_field_size
from apps.system.uploads import validate_document_upload, validate_image_upload

from .models import Award, Book, Patent, Project, Publication, SoftwareCopyright, Standard


class PublicationSerializer(serializers.ModelSerializer):
    pdf_file_size = serializers.SerializerMethodField()

    class Meta:
        model = Publication
        fields = "__all__"

    def get_pdf_file_size(self, obj):
        return file_field_size(obj.pdf_file)

    def validate_pdf_file(self, value):
        return validate_document_upload(value)


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class PatentSerializer(serializers.ModelSerializer):
    pdf_file_size = serializers.SerializerMethodField()

    class Meta:
        model = Patent
        fields = "__all__"

    def get_pdf_file_size(self, obj):
        return file_field_size(obj.pdf_file)

    def validate_pdf_file(self, value):
        return validate_document_upload(value)


class SoftwareCopyrightSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoftwareCopyright
        fields = "__all__"


class AwardSerializer(serializers.ModelSerializer):
    image_size = serializers.SerializerMethodField()
    attachment_size = serializers.SerializerMethodField()

    class Meta:
        model = Award
        fields = "__all__"

    def get_image_size(self, obj):
        return file_field_size(obj.image)

    def get_attachment_size(self, obj):
        return file_field_size(obj.attachment)

    def validate_image(self, value):
        return validate_image_upload(value)

    def validate_attachment(self, value):
        return validate_document_upload(value)


class StandardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Standard
        fields = "__all__"


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"
