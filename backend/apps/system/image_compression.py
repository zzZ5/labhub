from dataclasses import dataclass
from io import BytesIO
from pathlib import PurePosixPath

from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models import ImageField
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image, ImageOps, UnidentifiedImageError


@dataclass(frozen=True)
class CompressionProfile:
    max_edge: int
    quality: int
    min_bytes: int
    prefer_webp: bool = True


DEFAULT_PROFILE = CompressionProfile(
    max_edge=getattr(settings, "IMAGE_COMPRESSION_MAX_EDGE", 1600),
    quality=getattr(settings, "IMAGE_COMPRESSION_QUALITY", 80),
    min_bytes=getattr(settings, "IMAGE_COMPRESSION_MIN_BYTES", 200 * 1024),
)

PROFILE_RULES = (
    (("avatars/", "members/avatars/"), CompressionProfile(640, 78, 80 * 1024)),
    (("portal/favicons/",), CompressionProfile(256, 88, 24 * 1024, prefer_webp=False)),
    (("portal/logos/",), CompressionProfile(1200, 88, 100 * 1024, prefer_webp=False)),
    (("portal/banners/", "portal/hero/"), CompressionProfile(1920, 82, 240 * 1024)),
    (("news/", "portal/research/", "publications/awards/"), CompressionProfile(1600, 80, 180 * 1024)),
    (("instruments/",), CompressionProfile(1400, 78, 150 * 1024)),
)


def image_fields(model):
    return [field for field in model._meta.fields if isinstance(field, ImageField)]


def profile_for_name(name):
    normalized = (name or "").replace("\\", "/").lower()
    for prefixes, profile in PROFILE_RULES:
        if normalized.startswith(prefixes):
            return profile
    return DEFAULT_PROFILE


def should_process(width, height, size, profile, force=False):
    return force or max(width, height) > profile.max_edge or size > profile.min_bytes


def output_format(image, profile):
    original = (image.format or "JPEG").upper()
    if not profile.prefer_webp:
        if original == "JPG":
            return "JPEG"
        return original if original in {"JPEG", "PNG", "WEBP"} else "PNG"
    return "WEBP"


def resize_image(image, profile):
    image = ImageOps.exif_transpose(image)
    if max(image.size) > profile.max_edge:
        image.thumbnail((profile.max_edge, profile.max_edge), Image.Resampling.LANCZOS)
    return image


def encode_image(image, fmt, profile):
    output = BytesIO()
    if fmt == "PNG":
        image.save(output, format="PNG", optimize=True, compress_level=9)
    elif fmt == "WEBP":
        image.save(output, format="WEBP", quality=profile.quality, method=6)
    else:
        if image.mode not in {"RGB", "L"}:
            image = image.convert("RGB")
        image.save(output, format="JPEG", quality=profile.quality, optimize=True, progressive=True)
    return output.getvalue()


def optimized_name(name, fmt):
    path = PurePosixPath(name)
    suffix = {"WEBP": ".webp", "JPEG": ".jpg", "PNG": ".png"}[fmt]
    return str(path.with_name(f"{path.stem}-optimized{suffix}"))


def compress_field_file(field_file, *, force=False):
    if not field_file or not getattr(field_file, "name", ""):
        return None

    storage = field_file.storage
    original_name = field_file.name
    profile = profile_for_name(original_name)
    try:
        original_size = storage.size(original_name)
        with storage.open(original_name, "rb") as source:
            with Image.open(source) as image:
                image.load()
                original_dimensions = image.size
                already_optimized = "-optimized" in PurePosixPath(original_name).stem
                if already_optimized and max(image.size) <= profile.max_edge:
                    return None
                if not should_process(*image.size, original_size, profile, force=force):
                    return None
                resized = resize_image(image, profile)
                fmt = output_format(image, profile)
                optimized = encode_image(resized, fmt, profile)
                optimized_dimensions = resized.size
    except (OSError, UnidentifiedImageError, ValueError):
        return None

    resized_image = optimized_dimensions != original_dimensions
    if len(optimized) >= original_size and not resized_image:
        return None

    try:
        saved_name = storage.save(optimized_name(original_name, fmt), ContentFile(optimized))
        field_file.name = saved_name
        if saved_name != original_name:
            storage.delete(original_name)
    except OSError:
        return None

    return {
        "original_name": original_name,
        "name": saved_name,
        "original_size": original_size,
        "size": len(optimized),
        "width": optimized_dimensions[0],
        "height": optimized_dimensions[1],
    }


def compress_instance_images(instance, *, force=False):
    changes = []
    for field in image_fields(instance.__class__):
        field_file = getattr(instance, field.name, None)
        result = compress_field_file(field_file, force=force)
        if not result:
            continue
        instance.__class__._default_manager.filter(pk=instance.pk).update(**{field.name: field_file.name})
        changes.append({"field": field.name, **result})
    return changes


@receiver(post_save, dispatch_uid="labhub_compress_uploaded_images")
def compress_uploaded_images(sender, instance, **kwargs):
    if not getattr(settings, "IMAGE_COMPRESSION_ENABLED", True):
        return
    if not hasattr(instance, "_meta") or instance.pk is None:
        return
    compress_instance_images(instance)
