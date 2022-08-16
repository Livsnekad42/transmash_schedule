from django.db import models

# from administration.services.constants import GEO_MODULE, USER_MODULE, COMPANY_MODULE, ADMIN_MODULE


class GeoModule(models.Model):
    # MODULE_MODELS = GEO_MODULE
    name = models.CharField(max_length=1, null=True, blank=True)

    def __str__(self):
        return "geo"

    @classmethod
    def model_name(cls):
        return cls.__name__.lower()


class UserModule(models.Model):
    # MODULE_MODELS = USER_MODULE
    name = models.CharField(max_length=1, null=True, blank=True)

    def __str__(self):
        return "users"

    @classmethod
    def model_name(cls):
        return cls.__name__.lower()


class CompanyModule(models.Model):
    # MODULE_MODELS = COMPANY_MODULE
    name = models.CharField(max_length=1, null=True, blank=True)

    def __str__(self):
        return "company"

    @classmethod
    def model_name(cls):
        return cls.__name__.lower()


class AdminModule(models.Model):
    # MODULE_MODELS = ADMIN_MODULE
    name = models.CharField(max_length=1, null=True, blank=True)

    def __str__(self):
        return "admin"

    @classmethod
    def model_name(cls):
        return cls.__name__.lower()
