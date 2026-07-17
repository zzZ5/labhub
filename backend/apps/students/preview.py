import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from django.core.files.base import ContentFile

OFFICE_EXTENSIONS = {
    ".doc",
    ".docx",
    ".odp",
    ".ods",
    ".odt",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
}


def is_office_preview_candidate(filename: str) -> bool:
    return Path(filename).suffix.lower() in OFFICE_EXTENSIONS


def refresh_file_preview_pdf(instance, *, source_field="file", preview_field="preview_pdf") -> bool:
    file_field = getattr(instance, source_field)
    preview_pdf = getattr(instance, preview_field)
    filename = instance.original_filename or Path(file_field.name).name
    if not file_field or not is_office_preview_candidate(filename):
        instance.preview_status = "none"
        instance.preview_error = ""
        instance.save(update_fields=["preview_status", "preview_error"])
        return False

    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        instance.preview_status = "failed"
        instance.preview_error = "服务器未安装 LibreOffice，暂不能生成 PDF 预览。"
        instance.save(update_fields=["preview_status", "preview_error"])
        return False

    instance.preview_status = "pending"
    instance.preview_error = ""
    instance.save(update_fields=["preview_status", "preview_error"])

    suffix = Path(filename).suffix.lower()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        profile_path = temp_path / "libreoffice-profile"
        profile_path.mkdir()
        source_path = temp_path / f"source{suffix}"
        with file_field.open("rb") as file_obj:
            source_path.write_bytes(file_obj.read())

        conversion_source = source_path
        if suffix == ".docx":
            try:
                from docx import Document as WordDocument

                normalized_dir = temp_path / "normalized"
                normalized_dir.mkdir()
                conversion_source = normalized_dir / source_path.name
                WordDocument(source_path).save(conversion_source)
            except Exception:
                conversion_source = source_path

        command = [
            soffice,
            f"-env:UserInstallation={profile_path.as_uri()}",
            "--headless",
            "--nologo",
            "--nodefault",
            "--nolockcheck",
            "--nofirststartwizard",
            "--norestore",
            "--convert-to",
            "pdf",
            "--outdir",
            str(temp_path),
            str(conversion_source),
        ]
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                timeout=90,
                env={**os.environ, "HOME": str(temp_path), "SAL_USE_VCLPLUGIN": "svp"},
            )
        except subprocess.TimeoutExpired:
            instance.preview_status = "failed"
            instance.preview_error = "PDF 预览生成超时，请下载原文件查看。"
            instance.save(update_fields=["preview_status", "preview_error"])
            return False

        output_pdf = temp_path / "source.pdf"
        if completed.returncode != 0 or not output_pdf.exists():
            message = (completed.stderr or completed.stdout or b"").decode("utf-8", errors="ignore").strip()
            message = "\n".join(line for line in message.splitlines() if "javaldx" not in line.lower()).strip()
            if "source file could not be loaded" in message.lower():
                message = "源文件无法读取，请确认文件完整后重新上传。"
            instance.preview_status = "failed"
            instance.preview_error = (message or "PDF 预览生成失败，请下载原文件查看。")[:240]
            instance.save(update_fields=["preview_status", "preview_error"])
            return False

        preview_name = f"{Path(file_field.name).stem}.pdf"
        if preview_pdf:
            preview_pdf.delete(save=False)
        preview_pdf.save(preview_name, ContentFile(output_pdf.read_bytes()), save=False)
        instance.preview_status = "ready"
        instance.preview_error = ""
        instance.save(update_fields=[preview_field, "preview_status", "preview_error"])
        return True


def refresh_archive_preview_pdf(archive_file) -> bool:
    return refresh_file_preview_pdf(archive_file)
