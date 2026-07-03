from django.conf import settings
from rest_framework import serializers


def format_size(size):
    if size >= 1024 * 1024:
        return f"{size / 1024 / 1024:.0f} MB"
    if size >= 1024:
        return f"{size / 1024:.0f} KB"
    return f"{size} B"


def validate_upload_size(file_obj):
    max_size = getattr(settings, "MAX_UPLOAD_SIZE", 200 * 1024 * 1024)
    if file_obj and getattr(file_obj, "size", 0) > max_size:
        raise serializers.ValidationError(f"文件过大，当前上限为 {format_size(max_size)}。请压缩后重新上传，或联系管理员调整上传限制。")
    return file_obj
