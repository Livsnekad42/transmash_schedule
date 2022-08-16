from django.db import models
from django.utils.translation import gettext_lazy as _


class Country(models.Model):
    code = models.CharField(_('country code'), max_length=10, primary_key=True)
    name = models.CharField(_('country name'), max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('country')
        verbose_name_plural = _('countries')


class Region(models.Model):
    name = models.CharField(_('region name'), max_length=255)
    code = models.CharField(_('reqion code'), db_index=True, max_length=10, null=True, blank=True)
    federal_district = models.CharField(max_length=125, null=True, blank=True)
    region_kladr_id = models.CharField(db_index=True, max_length=20, null=True, blank=True)
    region_iso_code = models.CharField(db_index=True, max_length=20, null=True, blank=True)
    region_type_full = models.CharField(db_index=True, max_length=50, null=True, blank=True)
    country = models.ForeignKey(Country, related_name='regions', on_delete=models.CASCADE)

    def to_json(self):
        return {
            "id": self.id,
            "country": self.country.name,
            "name": self.name,
        }

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('region')
        verbose_name_plural = _('regions')
        unique_together = (('country', 'name'),)


class City(models.Model):
    region = models.ForeignKey(Region, related_name='cities', on_delete=models.CASCADE, null=True)
    name = models.CharField(_('city name'), max_length=255)
    latitude = models.DecimalField(max_digits=21, decimal_places=18, blank=True, null=True)
    longitude = models.DecimalField(max_digits=21, decimal_places=18, blank=True, null=True)
    timezone = models.CharField(_('time zone'), max_length=10, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('city')
        verbose_name_plural = _('cities')
        unique_together = (('region', 'name'),)
        ordering = ['name']

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "lat": float(self.latitude) if self.latitude else 0.0,
            "lng": float(self.longitude) if self.longitude else 0.0,
            "timezone": self.timezone,
        }


class Street(models.Model):
    city = models.ForeignKey(City, related_name='streets', on_delete=models.CASCADE, null=True)
    street_type = models.CharField(_("street type"), max_length=10, default="ул")
    street = models.CharField(_("street"), max_length=250)


class Place(models.Model):
    city = models.ForeignKey(City, related_name='places', on_delete=models.CASCADE, null=True)
    place_name = models.CharField(_("place name"), max_length=250, blank=True, null=True)
    latitude = models.DecimalField(max_digits=21, decimal_places=18, blank=True, null=True)
    longitude = models.DecimalField(max_digits=21, decimal_places=18, blank=True, null=True)


class Address(models.Model):
    district = models.CharField(max_length=150, blank=True, null=True)
    home = models.CharField(max_length=10, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    street = models.ForeignKey(Street, related_name='addresses', on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=21, decimal_places=18, blank=True, null=True)
    longitude = models.DecimalField(max_digits=21, decimal_places=18, blank=True, null=True)

    def to_dict(self):
        return {
            "city": self.street.city.name,
            "district": self.district,
            "street": self.street.street,
            "home": self.home,
        }
