from django.contrib import admin

# Register your models here.
from geo_city.models import Country, Region, City, Address, Street, Place

admin.site.register(Country)
admin.site.register(Region)
admin.site.register(City)
admin.site.register(Street)
admin.site.register(Place)
admin.site.register(Address)
