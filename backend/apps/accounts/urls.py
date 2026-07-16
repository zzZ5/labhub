from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CurrentUserPasswordView, CurrentUserView, LoginView, LogoutView, RegisterView, RoleViewSet, UserAdminViewSet, seed_roles

router = DefaultRouter()
router.register("roles", RoleViewSet, basename="role")
router.register("users", UserAdminViewSet, basename="account-user")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/me/", CurrentUserView.as_view(), name="auth-me"),
    path("auth/password/", CurrentUserPasswordView.as_view(), name="auth-password"),
    path("roles/seed/", seed_roles, name="seed-roles"),
    path("", include(router.urls)),
]
