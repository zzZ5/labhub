from django.core.management.base import BaseCommand

from apps.documents.models import Document
from apps.students.models import StudentArchiveFile
from apps.students.preview import is_office_preview_candidate, refresh_file_preview_pdf


class Command(BaseCommand):
    help = "重新生成内部资料和学生归档资料的 Office 文件 PDF 预览。默认仅处理失败项。"

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="重新生成全部 Office 文件预览，而不仅是失败项。",
        )

    def handle(self, *args, **options):
        scanned = succeeded = failed = skipped = 0
        models = (Document, StudentArchiveFile)

        for model in models:
            queryset = model.objects.all() if options["all"] else model.objects.filter(preview_status="failed")
            for instance in queryset.iterator():
                scanned += 1
                filename = instance.original_filename or instance.file.name
                if not is_office_preview_candidate(filename):
                    skipped += 1
                    continue

                try:
                    converted = refresh_file_preview_pdf(instance)
                except Exception as exc:
                    failed += 1
                    self.stderr.write(self.style.ERROR(f"[{model.__name__} #{instance.pk}] {filename}: {exc}"))
                    continue

                if converted:
                    succeeded += 1
                    self.stdout.write(f"[{model.__name__} #{instance.pk}] 已生成：{filename}")
                else:
                    failed += 1
                    instance.refresh_from_db(fields=["preview_error"])
                    self.stderr.write(
                        self.style.WARNING(
                            f"[{model.__name__} #{instance.pk}] 失败：{filename}；{instance.preview_error or '未知错误'}"
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"预览重建完成：扫描 {scanned}，成功 {succeeded}，失败 {failed}，跳过 {skipped}。"
            )
        )
