import csv
import os

from django.core.management.base import BaseCommand
from geo_city.models import Country, Region, City


class Command(BaseCommand):
    help = 'Import all'

    countries_indexs = [1, 2, 3, 4, 5, 6, 7, 11, 12, 13, 14, 15, 16, 17, 18]

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, action='store', required=True)

    def handle(self, *args, **options):
        path = options.get('path')
        if path is not None:
            with open(os.path.join(path, '_countries.csv'), 'r', encoding="utf8") as countryFile:
                country_reader = csv.reader(countryFile, delimiter=';')
                next(country_reader)
                countries = []
                for row in country_reader:
                    if row[0] and row[1]:
                        if int(row[0]) in self.countries_indexs:
                            code = row[0]
                            name = row[1]
                            countries.append(Country(code=code, name=name))
                Country.objects.bulk_create(countries, 999)

            with open(os.path.join(path, '_regions.csv'), 'r', encoding="utf8") as regionFile:
                region_reader = csv.reader(regionFile, delimiter=';')
                next(region_reader)
                regions = []
                for row in region_reader:
                    if row[0] and row[1] and row[2]:
                        if int(row[1]) in self.countries_indexs:
                            code = row[0]
                            country_code = row[1]
                            name = row[2]
                            country = Country.objects.get(code=country_code)
                            regions.append(Region(code=code, country=country, name=name))
                Region.objects.bulk_create(regions, 999, True)

            with open(os.path.join(path, path, 'cis_towns.csv'), 'r', encoding="utf8") as cityFile:
                city_reader = csv.reader(cityFile, delimiter=';')
                next(city_reader)
                cities = []
                timezone = None
                latitude = None
                longitude = None
                for row in city_reader:
                    if row[2] and row[3]:
                        region_code = row[2]
                        name = row[3]
                    if len(row) > 4:
                        if row[4] in row:
                            timezone = row[4]
                        if row[5] in row:
                            latitude = row[5]
                        if row[6] in row:
                            longitude = row[6]
                    region = Region.objects.get(code=region_code)
                    cities.append(
                        City(region=region, name=name, timezone=timezone, latitude=latitude, longitude=longitude))
                City.objects.bulk_create(cities, 999, True)
