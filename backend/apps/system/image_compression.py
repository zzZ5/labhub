from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models import ImageField
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image, ImageOps, UnidentifiedImageError


MAX_EDGE = getattr(settings, "IMAGE_COMPRESSION_MAX_EDGE", 2000)
QUALITY = getattr(settings, "IMAGE_COMPRESSION_QUALITY", 82)
MIN_BYTES = getattr(settings, "IMAGE_COMPRESSION_MIN_BYTES", 320 * 1024)


def image_fields(model):
    return [field for field in model._meta.fields if isinstance(field, ImageField)]


def should_process(width, height, size):
    return max(width, height) > MAX_EDGE or size > MIN_BYTES


def output_format(image, original_format):
    fmt = (original_format or "JPEG").upper()
    if fmt == "JPG":
        return "JPEG"
    if fmt in {"JPEG", "PNG", "WEBP"}:
        return fmt
    return "JPEG"


def resize_image(image):
    image = ImageOps.exif_transpose(image)
    if max(image.size) <= MAX_EDGE:
        return image
    image.thumbnail((MAX_EDGE, MAX_EDGE), Image.Resampling.LANCZOS)
    return image


def encode_image(image, fmt):
    output = BytesIO()
    if fmt == "PNG":
        image.save(output, format="PNG", optimize=True)
    elif fmt == "WEBP":
        image.save(output, format="WEBP", quality=QUALITY, method=6)
    else:
        if image.mode not in {"RGB", "L"}:
            image = image.convert("RGB")
        image.save(output, format="JPEG", quality=QUALITY, optimize=True, progressive=True)
    return output.getvalue()


def compress_field_file(field_file):
    if not field_file or not getattr(field_file, "name", ""):
        return

    storage = field_file.storage
    name = field_file.name
    try:
        size = storage.size(name)
    except OSError:
        return

    try:
        with storage.open(name, "rb") as source:
            with Image.open(source) as image:
                image.load()
                resize_needed = max(image.width, image.height) > MAX_EDGE
                if not should_process(image.width, image.height, size):
                    return
                fmt = output_format(image, image.format)
                optimized = encode_image(resize_image(image), fmt)
    except (OSError, UnidentifiedImageError, ValueError):
        return

    if len(optimized) >= size and not resize_needed:
        return

    try:
        storage.delete(name)
        storage.save(name, ContentFile(optimized))
    except OSError:
        return


@receiver(post_save, dispatch_uid="labhub_compress_uploaded_images")
def compress_uploaded_images(sender, instance, **kwargs):
    if not getattr(settings, "IMAGE_COMPRESSION_ENABLED", True):
        return
    if not hasattr(instance, "_meta"):
        return
    for field in image_fields(sender):
        compress_field_file(getattr(instance, field.name, None))
