from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from .models import Role, UserProfile, UserRole
from .services import user_role_codes

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "real_name",
            "avatar",
            "phone",
            "role_type",
            "bio",
            "is_approved",
            "approved_by",
            "approved_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["role_type", "is_approved", "approved_by", "approved_at", "created_at", "updated_at"]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "is_active", "is_staff", "is_superuser", "profile", "roles"]
        read_only_fields = ["id", "is_staff", "is_superuser", "roles"]

    def get_roles(self, obj):
        return sorted(user_role_codes(obj))


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    real_name = serializers.CharField(required=False, allow_blank=True, max_length=80)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=30)

    class Meta:
        model = User
        fields = ["username", "email", "password", "real_name", "phone"]

    def create(self, validated_data):
        real_name = validated_data.pop("real_name", "")
        phone = validated_data.pop("phone", "")
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data, password=password)
        profile = user.profile
        profile.real_name = real_name
        profile.phone = phone
        profile.save(update_fields=["real_name", "phone", "updated_at"])
        return user


class AdminUserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True, max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    real_name = serializers.CharField(required=False, allow_blank=True, max_length=80)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=30)
    role_type = serializers.CharField(default="member")
    is_approved = serializers.BooleanField(default=True)
    system_roles = serializers.ListField(child=serializers.CharField(), required=False, default=list)

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("该邮箱已存在。")
        return email

    def validate_username(self, value):
        username = value.strip()
        if username and User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError("该账号名已存在。")
        return username

    def validate_role_type(self, value):
        allowed = {"member", "master", "phd", "undergraduate", "postdoc", "pi", "other"}
        if value not in allowed:
            raise serializers.ValidationError("学校身份不正确。")
        return value

    def validate_system_roles(self, value):
        allowed = {"editor", "document_manager", "instrument_manager", "admin"}
        invalid = [role for role in value if role not in allowed]
        if invalid:
            raise serializers.ValidationError(f"系统权限不正确：{', '.join(invalid)}")
        return list(dict.fromkeys(value))

    def create(self, validated_data):
        system_roles = validated_data.pop("system_roles", [])
        real_name = validated_data.pop("real_name", "")
        phone = validated_data.pop("phone", "")
        role_type = validated_data.pop("role_type", "member")
        is_approved = validated_data.pop("is_approved", True)
        password = validated_data.pop("password")
        username = validated_data.pop("username", "") or validated_data["email"]
        user = User.objects.create_user(username=username, password=password, **validated_data)
        profile = user.profile
        profile.real_name = real_name
        profile.phone = phone
        profile.role_type = role_type
        profile.is_approved = is_approved
        request = self.context.get("request")
        if is_approved and request:
            from django.utils import timezone

            profile.approved_by = request.user
            profile.approved_at = timezone.now()
        profile.save()

        role_codes = [role_type, *system_roles]
        roles = Role.objects.filter(code__in=role_codes)
        for role in roles:
            UserRole.objects.get_or_create(user=user, role=role, defaults={"assigned_by": getattr(request, "user", None)})
        return user


class AdminUserUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True, max_length=150)
    email = serializers.EmailField(required=False)
    real_name = serializers.CharField(required=False, allow_blank=True, max_length=80)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=30)
    role_type = serializers.CharField(required=False)
    is_approved = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)

    def validate_email(self, value):
        email = value.strip().lower()
        user = self.context["user"]
        if User.objects.filter(email__iexact=email).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("该邮箱已存在。")
        return email

    def validate_username(self, value):
        username = value.strip()
        user = self.context["user"]
        if username and User.objects.filter(username__iexact=username).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("该账号名已存在。")
        return username

    def validate_role_type(self, value):
        allowed = {"member", "master", "phd", "undergraduate", "postdoc", "pi", "other"}
        if value not in allowed:
            raise serializers.ValidationError("学校身份不正确。")
        return value

    def update(self, instance, validated_data):
        profile_data = {
            key: validated_data.pop(key)
            for key in ["real_name", "phone", "role_type", "is_approved"]
            if key in validated_data
        }
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        profile = instance.profile
        for field, value in profile_data.items():
            setattr(profile, field, value)
        request = self.context.get("request")
        if profile_data.get("is_approved") is True and request:
            from django.utils import timezone

            profile.approved_by = request.user
            profile.approved_at = profile.approved_at or timezone.now()
        elif profile_data.get("is_approved") is False:
            profile.approved_by = None
            profile.approved_at = None
        profile.save()

        real_name = profile_data.get("real_name")
        try:
            student_profile = instance.student_profile
        except ObjectDoesNotExist:
            student_profile = None
        if real_name is not None and student_profile and student_profile.name != real_name:
            student_profile.name = real_name
            student_profile.save(update_fields=["name", "updated_at"])
        return instance


class AdminPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        request = self.context.get("request")
        username = attrs["username"].strip()
        password = attrs["password"]
        user = authenticate(request=request, username=username, password=password)
        if user is None:
            matched_user = User.objects.filter(email__iexact=username).first()
            if matched_user:
                user = authenticate(request=request, username=matched_user.get_username(), password=password)
        if user is None:
            raise serializers.ValidationError("账号名/邮箱或密码错误。")
        if not user.is_active:
            raise serializers.ValidationError("账号已被停用。")
        attrs["user"] = user
        return attrs


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "code", "description", "is_system", "created_at"]
        read_only_fields = ["id", "created_at"]


class UserApprovalSerializer(serializers.Serializer):
    is_approved = serializers.BooleanField()
    role_type = serializers.CharField(required=False)


class UserRoleAssignSerializer(serializers.Serializer):
    role_code = serializers.CharField()

    def validate_role_code(self, value):
        if not Role.objects.filter(code=value).exists():
            raise serializers.ValidationError("角色不存在。")
        return value
