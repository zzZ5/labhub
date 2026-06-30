from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class ProtectedMediaStorage(FileSystemStorage):
    def __init__(self):
        super().__init__(location=settings.PROTECTED_MEDIA_ROOT, base_url=None)
