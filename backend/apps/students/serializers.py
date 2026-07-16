from rest_framework import serializers

from apps.accounts.models import RoleCode
from apps.system.serializer_fields import file_field_size
from apps.system.uploads import validate_upload_size

from .models import StudentArchiveFile, StudentProfile
from .services import can_delete_archive_file, can_delete_student_profile, can_edit_student_profile


class StudentArchiveFileSerializer(serializers.ModelSerializer):
    file_type_label = serializers.CharField(source="get_file_type_display", read_only=True)
    file_size = serializers.SerializerMethodField()
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
            "file_size",
            "preview_pdf",
            "preview_status",
            "preview_error",
            "original_filename",
            "uploaded_by",
            "uploaded_at",
            "description",
            "can_delete",
        ]
        read_only_fields = ["uploaded_by", "uploaded_at", "original_filename", "preview_pdf", "preview_status", "preview_error"]

    def get_file_size(self, obj):
        return file_field_size(obj.file)

    def get_can_delete(self, obj):
        request = self.context.get("request")
        return can_delete_archive_file(getattr(request, "user", None), obj)

    def validate_file(self, file_obj):
        return validate_upload_size(file_obj)


class StudentProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    avatar_size = serializers.SerializerMethodField()
    avatar_upload = serializers.ImageField(write_only=True, required=False)
    degree_label = serializers.CharField(source="get_degree_type_display", read_only=True)
    supervisor_name = serializers.CharField(source="supervisor.profile.real_name", read_only=True)
    user_display_name = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_username = serializers.CharField(source="user.username", read_only=True)
    supervisor_email = serializers.EmailField(source="supervisor.email", read_only=True)
    advisor_names = serializers.SerializerMethodField()
    advisor_emails = serializers.SerializerMethodField()
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
            "avatar",
            "avatar_size",
            "avatar_upload",
            "name",
            "degree_type",
            "degree_label",
            "grade",
            "supervisor",
            "supervisor_name",
            "supervisor_email",
            "advisors",
            "advisor_names",
            "advisor_emails",
            "research_topic",
            "research_direction",
            "enrollment_date",
            "graduation_date",
            "destination",
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

    def get_avatar_size(self, obj):
        profile = getattr(obj.user, "profile", None)
        return file_field_size(getattr(profile, "avatar", None))

    def get_avatar(self, obj):
        profile = getattr(obj.user, "profile", None)
        avatar = getattr(profile, "avatar", None)
        return avatar.url if avatar else ""

    def validate_avatar_upload(self, file_obj):
        return validate_upload_size(file_obj)

    def validate_user(self, user):
        profile = getattr(user, "profile", None)
        identity = getattr(profile, "school_identity", "")
        student_roles = {RoleCode.UNDERGRADUATE, RoleCode.MASTER, RoleCode.PHD}
        if identity in student_roles:
            return user
        raise serializers.ValidationError("学生档案只能关联本科生、硕士或博士账号。")

    def create(self, validated_data):
        avatar = validated_data.pop("avatar_upload", None)
        advisors = validated_data.pop("advisors", [])
        if not advisors and validated_data.get("supervisor"):
            advisors = [validated_data["supervisor"]]
        if advisors and not validated_data.get("supervisor"):
            validated_data["supervisor"] = advisors[0]
        instance = super().create(validated_data)
        instance.advisors.set(advisors)
        self._sync_user_profile_name(instance)
        self._sync_user_avatar(instance, avatar)
        return instance

    def update(self, instance, validated_data):
        avatar = validated_data.pop("avatar_upload", None)
        advisors = validated_data.pop("advisors", None)
        if advisors and not validated_data.get("supervisor"):
            validated_data["supervisor"] = advisors[0]
        instance = super().update(instance, validated_data)
        if advisors is not None:
            instance.advisors.set(advisors)
        self._sync_user_profile_name(instance)
        self._sync_user_avatar(instance, avatar)
        return instance

    def get_advisor_names(self, obj):
        names = []
        for user in obj.advisors.all():
            profile = getattr(user, "profile", None)
            names.append(getattr(profile, "real_name", "") or user.get_full_name() or user.get_username())
        if not names and obj.supervisor:
            profile = getattr(obj.supervisor, "profile", None)
            names.append(getattr(profile, "real_name", "") or obj.supervisor.get_full_name() or obj.supervisor.get_username())
        return names

    def get_advisor_emails(self, obj):
        emails = [user.email for user in obj.advisors.all() if user.email]
        if not emails and obj.supervisor and obj.supervisor.email:
            emails.append(obj.supervisor.email)
        return emails

    def _sync_user_profile_name(self, instance):
        profile = getattr(instance.user, "profile", None)
        if profile and profile.real_name != instance.name:
            profile.real_name = instance.name
            profile.save(update_fields=["real_name", "updated_at"])

    def _sync_user_avatar(self, instance, avatar):
        profile = getattr(instance.user, "profile", None)
        if profile and avatar:
            profile.avatar = avatar
            profile.save(update_fields=["avatar", "updated_at"])
