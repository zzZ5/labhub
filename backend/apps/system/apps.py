from django.apps import AppConfig


class SystemConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.system"
    verbose_name = "系统配置"

    def ready(self):
        from . import image_compression  # noqa: F401
