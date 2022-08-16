import pprint

from django.test import TestCase
from geo_city.models import City, Country, Region, Street
from geo_city.serializers import PlaceSerializer, AddressSerializer, StreetSerializer


class StreetSerializerTests(TestCase):


    def test_is_valid_street(self):
        country = Country.objects.create(code=91595, name='Russia1234')
        region = Region.objects.create(code=23456, name='Birobijan1234', country=country)
        city = City.objects.create(name='Astana1234', region=region, latitude="56.253274100", longitude="51.283364200",
                                   timezone="UTC+3")
        print(city.id)
        street = 'Ленина'
        street_instance = Street.objects.create(city=city, street=street)

        # street_instance.is_valid(raise_exception=True)
        # street_serializer = StreetSerializer(validated_data=street_instance)

    # self.assertTrue(street_serializer.is_valid())

    # instance = street_serializer.save()
    # self.assertTrue(instance.pk)


