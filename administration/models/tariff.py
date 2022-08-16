from django.db import models
from django.utils.translation import gettext_lazy as _

from administration.models.partner import Partner
from core.model_fields.currency import CurrencyField
from core.models import TimestampedModel


class TariffPlane(TimestampedModel):
    title = models.CharField(max_length=200)
    price = CurrencyField()
    is_archive = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ['-created_at', '-updated_at']


class CompanyBilling(models.Model):
    number_managers = models.IntegerField(default=0)
    number_established_branches = models.IntegerField(default=0)
    number_megabytes_disk = models.IntegerField(default=0)
    number_goods_services = models.IntegerField(default=0)
    notification = models.BooleanField(default=False)
    landing = models.BooleanField(default=False)
    report = models.BooleanField(default=False)
    number_tasks = models.IntegerField(default=0)
    documents_template = models.BooleanField(default=False)
    analytics = models.BooleanField(default=False)
    dashboard = models.BooleanField(default=False)


class UserBilling(models.Model):
    number_family_tree_nodes = models.IntegerField(default=0)
    number_megabytes_disk = models.IntegerField(default=0)
    number_memory_page = models.IntegerField(default=0)


class CompanyPlan(TariffPlane):
    tariff = models.ForeignKey(CompanyBilling, related_name="company_plan", on_delete=models.CASCADE)


class UserPlan(TariffPlane):
    tariff = models.ForeignKey(UserBilling, related_name="user_plan", on_delete=models.CASCADE)


class PromoCodes(TimestampedModel):
    code = models.CharField(max_length=25)
    expiration_date = models.DateField(null=True, blank=True)
    discount = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    tariff = models.ForeignKey(UserPlan, related_name="promo_codes", null=True, on_delete=models.CASCADE)
    partner = models.ForeignKey(Partner, related_name="promo_codes", on_delete=models.CASCADE)
