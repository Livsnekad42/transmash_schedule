import csv

from django.core.management.base import BaseCommand
from geo_city.models import Country, Region, City


class Command(BaseCommand):
    help = 'Import all'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, action='store', required=True)

    def handle(self, *args, **options):
        file_path = options.get('file')
        if not file_path:
            print("[!] Empty file")
            return

        region_map = {}
        cities = []
        country_instance, _ = Country.objects.get_or_create(code="RU", defaults={"name": "Россия"})

        with open(file_path, 'r', encoding="utf8") as data_file:
            data_reader = csv.reader(data_file, delimiter=';')
            next(data_reader)
            for row in data_reader:
                city_name = row[0]
                region_name = row[1]
                federal_district = row[2]
                lat = float(row[3].replace(",", "."))
                lng = float(row[4].replace(",", "."))

                if not region_map.get(region_name):
                    region_instance, _ = Region.objects.get_or_create(
                        name=region_name,
                        country=country_instance,
                        defaults={
                            "federal_district": federal_district,
                        },
                    )

                    region_map[region_name] = region_instance

                else:
                    region_instance = region_map[region_name]

                cities.append(City(name=city_name, region=region_instance, latitude=lat, longitude=lng))

        City.objects.bulk_create(cities, 999, True)
