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
    short_name = models.CharField(_('company short name'), max_length=50, null=True, blank=True)
    tagline = models.CharField(_('company tagline'), max_length=250, null=True, blank=True)
    slug = models.CharField(_('company slug'), max_length=100, null=True, blank=True)
    description = models.CharField(_('company description'), max_length=300, null=True, blank=True)
    inn = models.CharField(_('company inn'), max_length=35, null=True, blank=True)
    kpp = models.CharField(_('company kpp'), max_length=35, null=True, blank=True)
    ogrn = models.CharField(_('company ogrn'), max_length=35, null=True, blank=True)
    ogrn_date = models.DateField(null=True, blank=True)
    okato = models.CharField(_('company okato'), max_length=35, null=True, blank=True)
    oktmo = models.CharField(_('company oktmo'), max_length=35, null=True, blank=True)
    okpo = models.CharField(_('company okpo'), max_length=35, null=True, blank=True)
    okogu = models.CharField(_('company okogu'), max_length=35, null=True, blank=True)
    okfs = models.CharField(_('company okfs'), max_length=35, null=True, blank=True)
    okved = models.CharField(_('company okved'), max_length=35, null=True, blank=True)
    okved_type = models.CharField(_('company okved_type'), max_length=10, null=True, blank=True)
    type_company = models.CharField(_('company type'), max_length=20, choices=TYPES_COMPANY, null=True, blank=True)
    organizational_legal_form = models.ForeignKey(OrganizationalLegalForm, related_name="company",
                                                  null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=50, choices=STATUS, null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
    phone = models.CharField(max_length=18, db_index=True, null=True, blank=True)
    email = models.EmailField(null=True, db_index=True, blank=True)
    logo = models.ImageField(upload_to="companies/logo/", null=True, blank=True, validators=[validate_images])
    is_banned = models.BooleanField(default=False)
    tariff = models.ForeignKey(CompanyPlan, related_name='companies', null=True, on_delete=models.SET_NULL)

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
