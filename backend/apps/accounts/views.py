from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Role, UserRole
from .permissions import CanManageAccounts
from .serializers import (
    AdminPasswordResetSerializer,
    AdminUserCreateSerializer,
    AdminUserUpdateSerializer,
    CurrentUserPasswordChangeSerializer,
    CurrentUserProfileUpdateSerializer,
    LoginSerializer,
    RegisterSerializer,
    RoleSerializer,
    UserApprovalSerializer,
    UserRoleAssignSerializer,
    UserSerializer,
)
from .services import SYSTEM_PERMISSION_CODES, SYSTEM_ROLES

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        login(request, serializer.validated_data["user"])
        return Response(UserSerializer(serializer.validated_data["user"]).data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    @transaction.atomic
    def patch(self, request):
        serializer = CurrentUserProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data)


class CurrentUserPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CurrentUserPasswordChangeSerializer(data=request.data, context={"user": request.user})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        update_session_auth_hash(request, request.user)
        return Response({"detail": "密码已更新。"})


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Role.objects.filter(code__in=SYSTEM_PERMISSION_CODES).order_by("code")
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]


class UserAdminViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.select_related("profile").prefetch_related("user_roles__role").all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [CanManageAccounts]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    @action(detail=False, methods=["get"], url_path="pending")
    def pending(self, request):
        queryset = self.get_queryset().filter(profile__is_approved=False)
        return Response(UserSerializer(queryset, many=True).data)

    @action(detail=False, methods=["post"], url_path="create")
    @transaction.atomic
    def create_account(self, request):
        serializer = AdminUserCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"], url_path="update")
    @transaction.atomic
    def update_account(self, request, pk=None):
        user = self.get_object()
        if user == request.user and request.data.get("is_active") is False:
            return Response({"detail": "不能停用自己的账号。"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = AdminUserUpdateSerializer(user, data=request.data, partial=True, context={"request": request, "user": user})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data)

    @action(detail=True, methods=["post"], url_path="reset-password")
    @transaction.atomic
    def reset_password(self, request, pk=None):
        user = self.get_object()
        serializer = AdminPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data["password"])
        user.save(update_fields=["password"])
        return Response(UserSerializer(user).data)

    @action(detail=True, methods=["delete"], url_path="delete")
    @transaction.atomic
    def delete_account(self, request, pk=None):
        user = self.get_object()
        if user == request.user:
            return Response({"detail": "不能删除自己的账号。"}, status=status.HTTP_400_BAD_REQUEST)
        if user.is_superuser:
            return Response({"detail": "不能在这里删除超级管理员账号。"}, status=status.HTTP_400_BAD_REQUEST)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="approve")
    @transaction.atomic
    def approve(self, request, pk=None):
        user = self.get_object()
        serializer = UserApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = user.profile
        profile.is_approved = serializer.validated_data["is_approved"]
        if "school_identity" in serializer.validated_data:
            profile.school_identity = serializer.validated_data["school_identity"]
        if profile.is_approved:
            profile.approved_by = request.user
            from django.utils import timezone

            profile.approved_at = timezone.now()
        else:
            profile.approved_by = None
            profile.approved_at = None
        profile.save()
        return Response(UserSerializer(user).data)

    @action(detail=True, methods=["post"], url_path="roles")
    @transaction.atomic
    def assign_role(self, request, pk=None):
        user = self.get_object()
        serializer = UserRoleAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = Role.objects.get(code=serializer.validated_data["role_code"])
        UserRole.objects.get_or_create(user=user, role=role, defaults={"assigned_by": request.user})
        return Response(UserSerializer(user).data)

    @action(detail=True, methods=["delete"], url_path=r"roles/(?P<role_code>[^/.]+)")
    @transaction.atomic
    def remove_role(self, request, pk=None, role_code=None):
        user = self.get_object()
        if role_code not in SYSTEM_PERMISSION_CODES:
            return Response({"detail": "该项不是系统权限。"}, status=status.HTTP_400_BAD_REQUEST)
        if user == request.user and role_code == "admin":
            return Response({"detail": "不能移除自己的系统管理员角色。"}, status=status.HTTP_400_BAD_REQUEST)
        UserRole.objects.filter(user=user, role__code=role_code).delete()
        return Response(UserSerializer(user).data)


@api_view(["POST"])
@permission_classes([CanManageAccounts])
def seed_roles(request):
    for code, name, description in SYSTEM_ROLES:
        Role.objects.update_or_create(code=code, defaults={"name": name, "description": description, "is_system": True})
    return Response({"created": Role.objects.filter(code__in=SYSTEM_PERMISSION_CODES).count()})
