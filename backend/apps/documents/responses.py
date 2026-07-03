from pathlib import Path
from urllib.parse import quote

from django.conf import settings
from django.http import FileResponse, HttpResponse


def protected_file_response(file_field, filename="", *, as_attachment=False, content_type=None):
    filename = filename or Path(file_field.name).name
    disposition = "attachment" if as_attachment else "inline"
    accel_prefix = getattr(settings, "PROTECTED_MEDIA_ACCEL_PREFIX", "").strip()

    if accel_prefix:
        response = HttpResponse(content_type=content_type or "application/octet-stream")
        response["X-Accel-Redirect"] = f"{accel_prefix.rstrip('/')}/{quote(file_field.name)}"
        response["Content-Length"] = str(file_field.size)
    else:
        response = FileResponse(file_field.open("rb"), as_attachment=as_attachment, content_type=content_type)

    response["Content-Disposition"] = f"{disposition}; filename*=UTF-8''{quote(filename)}"
    return response
