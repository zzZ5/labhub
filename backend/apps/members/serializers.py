from rest_framework import serializers

from apps.system.serializer_fields import file_field_size

from .models import Member, MemberEducation, MemberExperience


class MemberEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberEducation
        fields = ["school", "degree", "major", "start_date", "end_date", "description"]


class MemberExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberExperience
        fields = ["organization", "position", "start_date", "end_date", "description"]


class MemberSerializer(serializers.ModelSerializer):
    educations = MemberEducationSerializer(many=True, read_only=True)
    experiences = MemberExperienceSerializer(many=True, read_only=True)
    role_label = serializers.SerializerMethodField()
    avatar_size = serializers.SerializerMethodField()

    def get_role_label(self, obj):
        legacy_labels = {
            "PI": "硕博导师",
            "teacher": "教师",
            "postdoc": "博士后",
            "phd": "博士生",
            "master": "硕士生",
            "undergraduate": "本科生",
            "alumni": "已毕业学生",
            "visitor": "访问学生",
        }
        return legacy_labels.get(obj.role_type, obj.role_type or "团队成员")

    def get_avatar_size(self, obj):
        return file_field_size(obj.avatar)

    class Meta:
        model = Member
        fields = [
            "id",
            "name",
            "name_en",
            "avatar",
            "avatar_size",
            "role_type",
            "role_label",
            "grade",
            "research_direction",
            "email",
            "profile",
            "join_date",
            "graduation_date",
            "destination",
            "sort_order",
            "educations",
            "experiences",
        ]
