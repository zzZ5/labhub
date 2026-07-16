from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import ImageField

from apps.system.image_compression import compress_instance_images


class Command(BaseCommand):
    help = "压缩数据库中已有的头像、横幅、新闻、成果和仪器图片。"

    def handle(self, *args, **options):
        scanned = optimized = bytes_before = bytes_after = 0
        for model in apps.get_models():
            if not any(isinstance(field, ImageField) for field in model._meta.fields):
                continue
            for instance in model._default_manager.iterator():
                scanned += 1
                for change in compress_instance_images(instance, force=True):
                    optimized += 1
                    bytes_before += change["original_size"]
                    bytes_after += change["size"]

        saved = max(bytes_before - bytes_after, 0)
        self.stdout.write(
            self.style.SUCCESS(
                f"图片优化完成：扫描 {scanned} 条记录，压缩 {optimized} 张，"
                f"由 {bytes_before / 1024 / 1024:.1f} MB 降至 {bytes_after / 1024 / 1024:.1f} MB，"
                f"节省 {saved / 1024 / 1024:.1f} MB。"
            )
        )
