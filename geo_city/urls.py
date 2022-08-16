from django.urls import path, include
from rest_framework.routers import DefaultRouter

from geo_city.views import CityViewSet, StreetViewSet, PlaceViewSet, AddressViewSet, SearchStreetApiView, \
    ReverseGeocodingApiView, SearchAddressApiView

router = DefaultRouter(trailing_slash=True)
router.register(r'city', CityViewSet)
router.register(r'street', StreetViewSet)
router.register(r'place', PlaceViewSet)
router.register(r'address', AddressViewSet)

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'search/street/', SearchStreetApiView.as_view(), name="geo_search_street"),
    path(r'search/address/', SearchAddressApiView.as_view(), name="geo_search_address"),
    path(r'search/reverse-geocoding', ReverseGeocodingApiView.as_view(), name="reverse_geocoding")
]
