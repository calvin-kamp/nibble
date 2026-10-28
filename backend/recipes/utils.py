"""Recipe images are stored without embedded metadata.

Photos carry EXIF (camera, time, GPS position), XMP and IPTC data. Copying only the
pixels into a new image drops all of it. The orientation tag goes too, so the pixels
are turned first and the image keeps showing the right way up. The colour profile
stays, it holds no personal data and keeps the colours as they were.
"""

from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

SAVE_OPTIONS = {
    "JPEG": {"quality": 90, "optimize": True},
    "PNG": {"optimize": True},
    "WEBP": {"quality": 90},
}

# Keys under which Pillow exposes metadata in Image.info
METADATA_KEYS = ("exif", "xmp", "XML:com.adobe.xmp", "photoshop", "iptc", "comment")


def has_metadata(image):
    """Whether an opened image still carries metadata, for cleaning stored files."""
    return (
        bool(image.getexif())
        or any(key in image.info for key in METADATA_KEYS)
        or bool(getattr(image, "text", None))
    )


def pixels_only(image):
    """A new image with the same pixels and nothing else; animations keep frame one."""
    image = ImageOps.exif_transpose(image)
    clean = Image.frombytes(image.mode, image.size, image.tobytes())

    if image.mode == "P":
        clean.putpalette(image.getpalette())

    # Transparent colour of palette and grey/RGB PNGs; not metadata, part of the picture
    if "transparency" in image.info:
        clean.info["transparency"] = image.info["transparency"]

    return clean


def encode_without_metadata(file, image_format):
    """Bytes of the image in the same format, without EXIF, XMP and IPTC."""
    file.seek(0)

    with Image.open(file) as image:
        image.load()
        icc_profile = image.info.get("icc_profile")
        clean = pixels_only(image)

    options = dict(SAVE_OPTIONS[image_format])

    if icc_profile:
        options["icc_profile"] = icc_profile

    buffer = BytesIO()
    clean.save(buffer, image_format, **options)

    return buffer.getvalue()


def without_metadata(file, image_format, name):
    """The uploaded file as a new ContentFile without metadata, ready to save."""
    return ContentFile(encode_without_metadata(file, image_format), name=name)
