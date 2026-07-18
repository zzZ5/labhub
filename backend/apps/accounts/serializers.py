from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from apps.system.serializer_fields import file_field_size
from apps.system.uploads import validate_avatar_upload as validate_avatar_size

from .models import Role, UserProfile, UserRole
from .services import SYSTEM_PERMISSION_CODES, user_role_codes

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    school_identity_label = serializers.CharField(source="get_school_identity_display", read_only=True)
    membership_status_label = serializers.CharField(source="get_membership_status_display", read_only=True)
    avatar_size = serializers.SerializerMethodField()

    def get_avatar_size(self, obj):
        return file_field_size(obj.avatar)

    def get_avatar(self, obj):
        return obj.avatar.url if obj.avatar else ""

    class Meta:
        model = UserProfile
        fields = [
            "real_name",
            "avatar",
            "avatar_size",
            "phone",
            "school_identity",
            "school_identity_label",
            "membership_status",
            "membership_status_label",
            "bio",
            "is_approved",
            "approved_by",
            "approved_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "school_identity",
            "membership_status",
            "is_approved",
            "approved_by",
            "approved_at",
            "created_at",
            "updated_at",
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "is_active", "is_staff", "is_superuser", "profile", "roles"]
        read_only_fields = ["id", "is_staff", "is_superuser", "roles"]

    def get_roles(self, obj):
        return sorted(user_role_codes(obj))


class CurrentUserProfileUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, max_length=150)
    real_name = serializers.CharField(required=False, allow_blank=True, max_length=80)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=30)
    bio = serializers.CharField(required=False, allow_blank=True)
    avatar = serializers.ImageField(required=False)

    def validate_avatar(self, value):
        return validate_avatar_size(value)

    def validate_username(self, value):
        username = value.strip()
        if not username:
            raise serializers.ValidationError("账号名不能为空。")
        user = self.instance
        if User.objects.filter(username__iexact=username).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("该账号名已被使用。")
        return username

    def update(self, instance, validated_data):
        username = validated_data.pop("username", None)
        if username is not None and username != instance.username:
            instance.username = username
            instance.save(update_fields=["username"])
        profile = instance.profile
        for field, value in validated_data.items():
            setattr(profile, field, value)
        profile.save()

        real_name = validated_data.get("real_name")
        try:
            student_profile = instance.student_profile
        except ObjectDoesNotExist:
            student_profile = None
        if real_name is not None and student_profile and student_profile.name != real_name:
            student_profile.name = real_name
            student_profile.save(update_fields=["name", "updated_at"])
        return instance


class CurrentUserPasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context["user"]
        if not user.check_password(value):
            raise serializers.ValidationError("当前密码不正确。")
        return value

    def validate_new_password(self, value):
        validate_password(value, self.context["user"])
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "两次输入的新密码不一致。"})
        if attrs["current_password"] == attrs["new_password"]:
            raise serializers.ValidationError({"new_password": "新密码不能与当前密码相同。"})
        return attrs


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
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    real_name = serializers.CharField(required=False, allow_blank=True, max_length=80)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=30)
    avatar = serializers.ImageField(required=False)
    school_identity = serializers.CharField(default=UserProfile.SchoolIdentity.OTHER)
    membership_status = serializers.CharField(default=UserProfile.MembershipStatus.ACTIVE)
    is_approved = serializers.BooleanField(default=True)
    system_roles = serializers.ListField(child=serializers.CharField(), required=False, default=list)

    def validate_email(self, value):
        email = value.strip().lower()
        if email and User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("该邮箱已存在。")
        return email

    def validate_username(self, value):
        username = value.strip()
        if username and User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError("该账号名已存在。")
        return username

    def validate_school_identity(self, value):
        if value not in UserProfile.SchoolIdentity.values:
            raise serializers.ValidationError("学校身份不正确。")
        return value

    def validate_membership_status(self, value):
        if value not in UserProfile.MembershipStatus.values:
            raise serializers.ValidationError("成员状态不正确。")
        return value

    def validate_avatar(self, value):
        return validate_avatar_size(value)

    def validate_system_roles(self, value):
        invalid = [role for role in value if role not in SYSTEM_PERMISSION_CODES]
        if invalid:
            raise serializers.ValidationError(f"系统权限不正确：{', '.join(invalid)}")
        return list(dict.fromkeys(value))

    def validate(self, attrs):
        email = attrs.get("email", "").strip().lower()
        username = attrs.get("username", "").strip()
        if not email and not username:
            raise serializers.ValidationError({"username": "邮箱和账号名至少填写一个。"})
        attrs["email"] = email
        attrs["username"] = username or email
        return attrs

    def create(self, validated_data):
        system_roles = validated_data.pop("system_roles", [])
        real_name = validated_data.pop("real_name", "")
        phone = validated_data.pop("phone", "")
        avatar = validated_data.pop("avatar", None)
        school_identity = validated_data.pop("school_identity", UserProfile.SchoolIdentity.OTHER)
        membership_status = validated_data.pop("membership_status", UserProfile.MembershipStatus.ACTIVE)
        is_approved = validated_data.pop("is_approved", True)
        password = validated_data.pop("password")
        username = validated_data.pop("username")
        user = User.objects.create_user(username=username, password=password, **validated_data)
        profile = user.profile
        profile.real_name = real_name
        profile.phone = phone
        if avatar:
            profile.avatar = avatar
        profile.school_identity = school_identity
        profile.membership_status = membership_status
        profile.is_approved = is_approved
        request = self.context.get("request")
        if is_approved and request:
            from django.utils import timezone

            profile.approved_by = request.user
            profile.approved_at = timezone.now()
        profile.save()

        roles = Role.objects.filter(code__in=system_roles)
        for role in roles:
            UserRole.objects.get_or_create(user=user, role=role, defaults={"assigned_by": getattr(request, "user", None)})
        return user


class AdminUserUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True, max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    real_name = serializers.CharField(required=False, allow_blank=True, max_length=80)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=30)
    avatar = serializers.ImageField(required=False)
    school_identity = serializers.CharField(required=False)
    membership_status = serializers.CharField(required=False)
    is_approved = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)

    def validate_email(self, value):
        email = value.strip().lower()
        user = self.context["user"]
        if email and User.objects.filter(email__iexact=email).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("该邮箱已存在。")
        return email

    def validate_username(self, value):
        username = value.strip()
        user = self.context["user"]
        if username and User.objects.filter(username__iexact=username).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("该账号名已存在。")
        return username

    def validate_school_identity(self, value):
        if value not in UserProfile.SchoolIdentity.values:
            raise serializers.ValidationError("学校身份不正确。")
        return value

    def validate_membership_status(self, value):
        if value not in UserProfile.MembershipStatus.values:
            raise serializers.ValidationError("成员状态不正确。")
        return value

    def validate_avatar(self, value):
        return validate_avatar_size(value)

    def validate(self, attrs):
        user = self.context["user"]
        email = attrs.get("email", user.email).strip().lower()
        username = attrs.get("username", user.username).strip()
        if not email and not username:
            raise serializers.ValidationError({"username": "邮箱和账号名至少保留一个。"})
        if "email" in attrs:
            attrs["email"] = email
        if "username" in attrs:
            attrs["username"] = username or email
        return attrs

    def update(self, instance, validated_data):
        profile_data = {
            key: validated_data.pop(key)
            for key in ["real_name", "phone", "avatar", "school_identity", "membership_status", "is_approved"]
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
    school_identity = serializers.ChoiceField(choices=UserProfile.SchoolIdentity.choices, required=False)


class UserRoleAssignSerializer(serializers.Serializer):
    role_code = serializers.CharField()

    def validate_role_code(self, value):
        if value not in SYSTEM_PERMISSION_CODES or not Role.objects.filter(code=value).exists():
            raise serializers.ValidationError("系统权限不存在。")
        return value
