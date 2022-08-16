import base64
import binascii
import secrets
from typing import Tuple

from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import gettext_lazy as _


MAX_UPLOAD_SIZE = getattr(settings, "MAX_UPLOAD_SIZE", 15)


def get_file_from_data_url(data_url) -> Tuple[ContentFile, Tuple[str, str]]:
    try:
        file_format, data_url = data_url.split(';base64,')
        _filename, _extension = secrets.token_hex(20), file_format.split('/')[-1]
        file = ContentFile(base64.b64decode(data_url), name=f"{_filename}.{_extension}")
    except (binascii.Error, ValueError, TypeError):
        raise ValidationError(_(f"Not valid Base64 format."))

    if file.size > MAX_UPLOAD_SIZE * 1024 * 1024:
        raise ValidationError(_(f"Max file size is {MAX_UPLOAD_SIZE}MB."))

    return file, (_filename, _extension)
