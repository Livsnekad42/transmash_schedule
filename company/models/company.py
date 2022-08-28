from enum import Enum

from django.db import models
from django.utils.translation import gettext_lazy as _

from administration.models import CompanyPlan
from core.converters.images import validate_images
from geo_city.models import Address
from profiles.models import Profile


class TypesCompany(Enum):
    LEGAL = "LEGAL"
    INDIVIDUAL = "INDIVIDUAL"


class StatusCompany(Enum):
    ACTIVE = "ACTIVE"
    LIQUIDATING = "LIQUIDATING"
    LIQUIDATED = "LIQUIDATED"
    BANKRUPT = "BANKRUPT"
    REORGANIZING = "REORGANIZING"


class OrganizationalLegalForm(models.Model):
    DIRECTORY_VERSION = (
        ("99", "99"),
        ("2012", "2012"),
        ("2014", "2014"),
    )
    directory_version = models.CharField(_('company type organization directory version'),
                                         choices=DIRECTORY_VERSION, max_length=6, null=True, blank=True)
    code = models.CharField(_('organization code'), max_length=15, null=True, blank=True)
    full = models.CharField(_('organization type full name'), max_length=150)
    short = models.CharField(_('organization short name'), max_length=10)


class Company(models.Model):
    TYPES_COMPANY = (
        (TypesCompany.LEGAL.value, 'legal'),
        (TypesCompany.INDIVIDUAL.value, 'individual'),
    )
    STATUS = (
        (StatusCompany.ACTIVE.value, "active"),
        (StatusCompany.LIQUIDATING.value, "liquidating"),
        (StatusCompany.LIQUIDATED.value, "liquidated"),
        (StatusCompany.BANKRUPT.value, "bankrupt"),
        (StatusCompany.REORGANIZING.value, "reorganizing"),
    )
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    name = models.CharField(_('company name'), db_index=True, max_length=150, null=True, blank=True)
    description = models.CharField(_('company description'), max_length=300, null=True, blank=True)
    type_company = models.CharField(_('company type'), max_length=20, choices=TYPES_COMPANY, null=True, blank=True)
    organizational_legal_form = models.ForeignKey(OrganizationalLegalForm, related_name="company",
                                                  null=True, on_delete=models.SET_NULL)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
    phone = models.CharField(max_length=18, db_index=True, null=True, blank=True)
    email = models.EmailField(null=True, db_index=True, blank=True)
    logo = models.ImageField(upload_to="companies/logo/", null=True, blank=True, validators=[validate_images])
    is_banned = models.BooleanField(default=False)

    # tariff = models.ForeignKey(CompanyPlan, related_name='companies', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('company')
        verbose_name_plural = _('companies')


class Branch(models.Model):
    name = models.CharField(_('branch name'), max_length=255, unique=True)
    company = models.ForeignKey(Company, related_name='branches', on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=18, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('branch')
        verbose_name_plural = _('branches')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address.to_dict(),
        }


class Department(models.Model):
    name = models.CharField(_('department name'), max_length=255, unique=True)
    company = models.ForeignKey(Company, related_name='departments', on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=18, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    class Meta:
        verbose_name = _('department')
        verbose_name_plural = _('departments')
