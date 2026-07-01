from rest_framework import serializers

from .models import (
    Instrument,
    InstrumentCategory,
    InstrumentFaultReport,
    InstrumentImage,
    InstrumentMaintenanceRecord,
    InstrumentTrainingRecord,
)
from .services import user_has_training


class InstrumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InstrumentCategory
        fields = ["id", "name", "slug", "description", "sort_order"]


class InstrumentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstrumentImage
        fields = ["id", "image", "caption", "sort_order"]


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
    training_passed = serializers.SerializerMethodField()

    class Meta:
        model = Instrument
        fields = [
            "id",
            "name",
            "model",
            "serial_number",
            "category",
            "category_id",
            "room",
            "location_detail",
            "manager_name",
            "image",
            "status",
            "status_label",
            "need_training",
            "notes",
            "sort_order",
            "training_passed",
        ]

    def get_training_passed(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        return user_has_training(user, obj) if user and user.is_authenticated else False


class InstrumentTrainingRecordSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.profile.real_name", read_only=True)
    instrument_name = serializers.CharField(source="instrument.name", read_only=True)

    class Meta:
        model = InstrumentTrainingRecord
        fields = "__all__"


class InstrumentMaintenanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstrumentMaintenanceRecord
        fields = "__all__"


class InstrumentFaultReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstrumentFaultReport
        fields = "__all__"
        read_only_fields = ["reporter", "handled_by", "handled_at", "result", "created_at"]
