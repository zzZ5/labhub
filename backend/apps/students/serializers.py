from rest_framework import serializers

from .models import StudentArchiveFile, StudentProfile
from .services import can_delete_archive_file, can_delete_student_profile, can_edit_student_profile, can_view_archive_file


class StudentArchiveFileSerializer(serializers.ModelSerializer):
    file_type_label = serializers.CharField(source="get_file_type_display", read_only=True)
    visibility_label = serializers.CharField(source="get_visibility_display", read_only=True)
    can_view = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = StudentArchiveFile
        fields = [
            "id",
            "student",
            "file_type",
            "file_type_label",
            "title",
            "file",
            "preview_pdf",
            "preview_status",
            "preview_error",
            "original_filename",
            "version",
            "visibility",
            "visibility_label",
            "uploaded_by",
            "uploaded_at",
            "description",
            "can_view",
            "can_delete",
        ]
        read_only_fields = ["uploaded_by", "uploaded_at", "original_filename", "preview_pdf", "preview_status", "preview_error"]

    def get_can_view(self, obj):
        request = self.context.get("request")
        return can_view_archive_file(getattr(request, "user", None), obj)

    def get_can_delete(self, obj):
        request = self.context.get("request")
        return can_delete_archive_file(getattr(request, "user", None), obj)


class StudentProfileSerializer(serializers.ModelSerializer):
    degree_label = serializers.CharField(source="get_degree_type_display", read_only=True)
    visibility_label = serializers.CharField(source="get_visibility_display", read_only=True)
    supervisor_name = serializers.CharField(source="supervisor.profile.real_name", read_only=True)
    user_display_name = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_username = serializers.CharField(source="user.username", read_only=True)
    supervisor_email = serializers.EmailField(source="supervisor.email", read_only=True)
    archive_files = StudentArchiveFileSerializer(many=True, read_only=True)
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = [
            "id",
            "user",
            "user_display_name",
            "user_email",
            "user_username",
            "name",
            "degree_type",
            "degree_label",
            "grade",
            "supervisor",
            "supervisor_name",
            "supervisor_email",
            "research_topic",
            "research_direction",
            "enrollment_date",
            "graduation_date",
            "destination",
            "visibility",
            "visibility_label",
            "created_at",
            "updated_at",
            "archive_files",
            "can_edit",
            "can_delete",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_can_edit(self, obj):
        request = self.context.get("request")
        return can_edit_student_profile(getattr(request, "user", None), obj)

    def get_can_delete(self, obj):
        request = self.context.get("request")
        return can_delete_student_profile(getattr(request, "user", None), obj)

    def get_user_display_name(self, obj):
        profile = getattr(obj.user, "profile", None)
        return getattr(profile, "real_name", "") or obj.user.get_full_name() or obj.user.get_username()

    def create(self, validated_data):
        instance = super().create(validated_data)
        self._sync_user_profile_name(instance)
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        self._sync_user_profile_name(instance)
        return instance

    def _sync_user_profile_name(self, instance):
        profile = getattr(instance.user, "profile", None)
        if profile and profile.real_name != instance.name:
            profile.real_name = instance.name
            profile.save(update_fields=["real_name", "updated_at"])
