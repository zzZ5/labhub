from rest_framework import serializers

from apps.system.serializer_fields import file_field_size
from apps.system.uploads import validate_image_upload

from .models import Instrument, InstrumentCategory


class InstrumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InstrumentCategory
        fields = ["id", "name", "slug", "description", "sort_order"]


class InstrumentSerializer(serializers.ModelSerializer):
    category = InstrumentCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=InstrumentCategory.objects.all(),
        source="category",
        required=False,
        allow_null=True,
        write_only=True,
    )
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    manager_name = serializers.CharField(source="manager.profile.real_name", read_only=True)
    image_size = serializers.SerializerMethodField()

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
            "manager_name",
            "image",
            "image_size",
            "status",
            "status_label",
            "notes",
            "sort_order",
            "created_at",
            "updated_at",
        ]

    def get_image_size(self, obj):
        return file_field_size(obj.image)

    def validate_image(self, value):
        return validate_image_upload(value)
