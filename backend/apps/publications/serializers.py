from rest_framework import serializers

from .models import Award, Book, Patent, Project, Publication, SoftwareCopyright, Standard


class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class PatentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patent
        fields = "__all__"


class SoftwareCopyrightSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoftwareCopyright
        fields = "__all__"


class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Award
        fields = "__all__"


class StandardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Standard
        fields = "__all__"


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"
