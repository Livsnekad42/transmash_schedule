from rest_framework import serializers
from rest_framework.fields import empty

from authentication.services.converter import phone_converter


class PhoneField(serializers.CharField):
    max_length = 25

    def run_validation(self, data=empty):
        data = super(PhoneField, self).run_validation(data)
        if data:
            return phone_converter(data)
        return data