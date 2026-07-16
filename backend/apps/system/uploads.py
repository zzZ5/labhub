from django.conf import settings
from rest_framework import serializers


MB = 1024 * 1024
DOCUMENT_UPLOAD_LIMIT = 200 * MB
SPREADSHEET_UPLOAD_LIMIT = 50 * MB
IMAGE_UPLOAD_LIMIT = 20 * MB
AVATAR_UPLOAD_LIMIT = 10 * MB
LOGO_UPLOAD_LIMIT = 5 * MB
FAVICON_UPLOAD_LIMIT = 2 * MB


def format_size(size):
    if size >= 1024 * 1024:
        return f"{size / 1024 / 1024:.0f} MB"
    if size >= 1024:
        return f"{size / 1024:.0f} KB"
    return f"{size} B"


def validate_upload_size(file_obj, max_size=None):
    max_size = max_size or getattr(settings, "MAX_UPLOAD_SIZE", DOCUMENT_UPLOAD_LIMIT)
    if file_obj and getattr(file_obj, "size", 0) > max_size:
        raise serializers.ValidationError(f"文件过大，当前上限为 {format_size(max_size)}。请压缩后重新上传，或联系管理员调整上传限制。")
    return file_obj


def validate_document_upload(file_obj):
    return validate_upload_size(file_obj, DOCUMENT_UPLOAD_LIMIT)


def validate_spreadsheet_upload(file_obj):
    return validate_upload_size(file_obj, SPREADSHEET_UPLOAD_LIMIT)


def validate_image_upload(file_obj):
    return validate_upload_size(file_obj, IMAGE_UPLOAD_LIMIT)


def validate_avatar_upload(file_obj):
    return validate_upload_size(file_obj, AVATAR_UPLOAD_LIMIT)


def validate_logo_upload(file_obj):
    return validate_upload_size(file_obj, LOGO_UPLOAD_LIMIT)


def validate_favicon_upload(file_obj):
    return validate_upload_size(file_obj, FAVICON_UPLOAD_LIMIT)
