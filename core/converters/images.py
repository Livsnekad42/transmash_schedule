import base64
import binascii
import io
import os
import secrets
from io import BytesIO
from pathlib import Path
from typing import Tuple

from PIL import Image, UnidentifiedImageError
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _
from django.db.models.fields.files import ImageFieldFile, ImageField

from core.slug import slug


MAX_UPLOAD_SIZE = getattr(settings, "MAX_UPLOAD_SIZE", 15)


image_types = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "gif": "GIF",
    "tif": "TIFF",
    "tiff": "TIFF",
}


def image_resize(image, width, height, file_name_suffix: str = None):
    img = Image.open(image)
    if img.width > width or img.height > height:
        output_size = (width, height)
        img.thumbnail(output_size)
        img_filename = Path(image.file.name).name
        img_suffix = Path(image.file.name).name.split(".")[-1]
        if file_name_suffix:
            img_filename = f'{".".join(img_filename.split(".")[:-1])}_{file_name_suffix}.{img_suffix}'
        img_format = image_types[img_suffix]
        buffer = BytesIO()
        img.save(buffer, format=img_format)
        return File(buffer, name=img_filename)
        # image.save(img_filename, file_object)


def _add_thumbs(s):
    parts = s.split('.')
    parts.insert(-1, 'thumb')
    res = '.'.join(parts)
    return res


def validate_images(field_file_obj):
    file_size = field_file_obj.file.size
    if file_size > MAX_UPLOAD_SIZE*1024*1024:
        raise ValidationError(_(f"Max file size is {MAX_UPLOAD_SIZE}MB"))


def get_img_from_data_url(data_url, resize=False, base_width=600, quality=50) -> Tuple[ContentFile, Tuple[str, str]]:
    try:
        file_format, data_url = data_url.split(';base64,')
        _filename, _extension = secrets.token_hex(20), file_format.split('/')[-1]
        file = ContentFile(base64.b64decode(data_url), name=f"{_filename}.{_extension}")
    except (binascii.Error, ValueError, TypeError):
        raise ValidationError(_(f"Not valid Base64 format."))

    if file.size > MAX_UPLOAD_SIZE * 1024 * 1024:
        raise ValidationError(_(f"Max file size is {MAX_UPLOAD_SIZE}MB."))

    try:
        image = Image.open(file).convert('RGB')
        image_io = io.BytesIO()
    except UnidentifiedImageError:
        raise ValidationError(_(f"Not valid Base64 format."))

    if resize:
        w_percent = (base_width/float(image.size[0]))
        h_size = int((float(image.size[1])*float(w_percent)))
        image = image.resize((base_width, h_size), Image.ANTIALIAS)

    image.save(image_io, format="JPEG", quality=quality, optimize=True)
    file = ContentFile(image_io.getvalue(), name=f"{_filename}.jpg")
    return file, (_filename, _extension)


class ThumbnailImageFile(ImageFieldFile):
    @property
    def get_thumb_url(self):
        return _add_thumbs(self.url)

    @property
    def _get_thumb_path(self):
        return _add_thumbs(self.path)

    def save(self, name, content, save=True):
        name_split = map(lambda x: slug(x), name.split('.'))
        name = '.'.join(name_split)
        super(ThumbnailImageFile, self).save(name, content, save)
        img = Image.open(self.path)
        img.thumbnail(
            (self.field.thumb_w, self.field.thumb_h),
            Image.ANTIALIAS
        )
        img.save(self._get_thumb_path)

    def delete(self, save=True):
        if os.path.exists(self._get_thumb_path):
            try:
                os.remove(self._get_thumb_path)
                os.remove(self.path)
            except:
                pass
        super(ThumbnailImageFile, self).delete(save)


class ThumbnailImageField(ImageField):
    attr_class = ThumbnailImageFile

    def __init__(self, thumb_w=256, thumb_h=256, *args, **kwargs):
        self.thumb_w = thumb_w
        self.thumb_h = thumb_h
        super(ThumbnailImageField, self).__init__(*args, **kwargs)