import exifread


def get_geolocation_from_image(file):
    exif = exifread.process_file(file)
    latitude = exif.get('GPS GPSLatitude', None)
    longitude = exif.get('GPS GPSLongitude', None)
    if latitude and longitude:
        try:
            latitude_string = latitude.printable
            longitude_string = longitude.printable
            lat_data = latitude_string[1:-1]
            lat_data = lat_data.split(', ')
            splitted_lat_data2 = lat_data[2].split("/")
            print(splitted_lat_data2)
            new_lat_data = int(splitted_lat_data2[0]) / int(splitted_lat_data2[1])
            data_longitude = longitude_string[1:-1]
            data_longitude = data_longitude.split(', ')
            splitted_longitude_data2 = data_longitude[2].split("/")
            print(splitted_longitude_data2)
            new_lon_data = int(splitted_longitude_data2[0]) / int(splitted_longitude_data2[1])
            lat = f"{lat_data[0]} {lat_data[1]}' {new_lat_data}\""
            lon = f"{data_longitude[0]} {data_longitude[1]}' {new_lon_data}\""
            return {"latitude": lat, "longitude": lon}
        except ZeroDivisionError:
            return None
    return None
