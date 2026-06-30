from rest_framework import serializers

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
    role_label = serializers.CharField(source="get_role_type_display", read_only=True)

    class Meta:
        model = Member
        fields = [
            "id",
            "name",
            "name_en",
            "avatar",
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
