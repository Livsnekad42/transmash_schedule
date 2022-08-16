import geocoder


def get_place_by_coordinates(latitude, longitude):
    geolocation = geocoder.osm('%s, %s' % (latitude, longitude))
    geolocation = geolocation.json
    region = geolocation.get('region', None)
    city = geolocation.get('city', None)
    if not city:
        city = geolocation.get('town', None)
    return {
        "region": region,
        "street": geolocation.get('street', None),
        "city": None,
        "neighborhood": geolocation.get('neighborhood', 'Место без названия'),
    }
