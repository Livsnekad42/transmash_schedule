from django.utils.translation import gettext_lazy as _

from rest_framework import serializers


class ImagesBase64Validator:
    message = _('Not valid Base64 format.')
    code = 'invalid'

    def __call__(self, value):
        if value:
            data = value.split(';base64,')
            if len(data) != 2:
                raise serializers.ValidationError(self.message, code=self.code)
        return value


class ImgBase64Field(serializers.CharField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validators.append(ImagesBase64Validator())
