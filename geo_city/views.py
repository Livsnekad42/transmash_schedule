import asyncio

from asgiref.sync import async_to_sync, sync_to_async
from django.utils.decorators import method_decorator
from rest_framework import mixins, viewsets, status
from rest_framework.exceptions import NotFound
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils.translation import gettext_lazy as _

from core.app_services.dadata import Point
from geo_city.filters import SearchFilterCityBackend, SearchFilterPlaceBackend, SearchFilterStreetBackend, \
    SearchFilterAddressBackend
from geo_city.models import City, Address, Street, Place
from geo_city.serializers import CitySerializer, AddressSerializer, StreetSerializer, PlaceSerializer, \
    SearchStreetListSerializer, ReverseGeocodingSerializer, SearchAddressListSerializer
from geo_city.services.data_converters.address import address_serializer
from geo_city.services.data_converters.street import street_serializer
from geo_city.services.get_street import get_valid_street, get_place_from_gps

LIMIT_QUERY = 20
LIMIT_RESULT_FROM_API = 8


class GeoCityGetterViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    def list(self, request, *args, **kwargs):
        # page = self.paginate_queryset(self.filter_queryset(self.get_queryset()))

        cities = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(cities)
        serializer = self.serializer_class(
            page,
            many=True
        )

        return self.get_paginated_response(serializer.data)
        # return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk):
        try:
            serializer_instance = self.queryset.filter(pk=pk).get()
        except self.serializer_class.Meta.models.DoesNotExist:
            raise NotFound(_('Not found.'))

        serializer = self.serializer_class(
            serializer_instance,
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class GeoCitySetterViewSet(
    mixins.CreateModelMixin,
):
    def create(self, request, *args, **kwargs):
        serializer_data = request.data

        serializer = self.serializer_class(
            data=serializer_data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk):
        try:
            serializer_instance = self.queryset.filter(pk=pk).get()
        except self.serializer_class.Meta.models.DoesNotExist:
            raise NotFound(_('Not found.'))

        serializer_data = request.data

        serializer = self.serializer_class(
            serializer_instance,
            data=serializer_data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CityViewSet(GeoCityGetterViewSet, viewsets.GenericViewSet,):
    queryset = City.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = CitySerializer
    filter_backends = (SearchFilterCityBackend, )


class StreetViewSet(GeoCityGetterViewSet, viewsets.GenericViewSet,):
    queryset = Street.objects.select_related("city")
    permission_classes = (IsAuthenticated,)
    serializer_class = StreetSerializer
    filter_backends = (SearchFilterStreetBackend, )


class PlaceViewSet(GeoCityGetterViewSet, GeoCitySetterViewSet, viewsets.GenericViewSet,):
    queryset = Place.objects.select_related("street", "street__city")
    permission_classes = (IsAuthenticated,)
    serializer_class = PlaceSerializer
    filter_backends = (SearchFilterPlaceBackend, )


class AddressViewSet(GeoCityGetterViewSet, viewsets.GenericViewSet,):
    queryset = Address.objects.select_related("street", "street__city")
    permission_classes = (IsAuthenticated,)
    serializer_class = AddressSerializer
    filter_backends = (SearchFilterAddressBackend, )


class SearchStreetApiView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SearchStreetListSerializer

    @method_decorator(async_to_sync)
    async def post(self, request):
        serializer_data = request.data

        serializer = self.serializer_class(
            data=serializer_data,
        )

        serializer.is_valid(raise_exception=True)

        data = await get_valid_street(serializer_data["city_name"], serializer_data["street"])
        if not data:
            return Response({'errors': {
                "detail": [_('Not found street data.')]
            }}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        result = []

        if len(data) > 0:
            tasks = []
            for street_data in data[:LIMIT_RESULT_FROM_API]:
                tasks.append(asyncio.create_task(street_serializer(street_data)))

            for _t in tasks:
                _street = await _t
                if _street:
                    result.append(_street.data)

        return Response(result, status=status.HTTP_200_OK)


class SearchAddressApiView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SearchAddressListSerializer

    @method_decorator(async_to_sync)
    async def post(self, request):
        serializer_data = request.data

        serializer = self.serializer_class(
            data=serializer_data,
        )

        serializer.is_valid(raise_exception=True)

        address = serializer_data["address"].split(" ")
        data = await get_valid_street(serializer_data["city_name"], *address)
        if not data:
            return Response({'errors': {
                "detail": [_('Not found address data.')]
            }}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        result = []

        if len(data) > 0:
            tasks = []
            for street_data in data[:LIMIT_RESULT_FROM_API]:
                tasks.append(asyncio.create_task(address_serializer(street_data)))

            for _t in tasks:
                _address = await _t
                if _address:
                    result.append(_address.data)
        # for add in result:
        #     print(add)
        return Response(result, status=status.HTTP_200_OK)


class ReverseGeocodingApiView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReverseGeocodingSerializer

    @method_decorator(async_to_sync)
    async def post(self, request):
        serializer_data = request.data

        serializer = self.serializer_class(
            data=serializer_data,
        )

        serializer.is_valid(raise_exception=True)

        point = Point(lat=serializer_data["lat"], lon=serializer_data["lng"])

        place = await get_place_from_gps(point)
        if not place:
            return Response({'errors': {
                "detail": [_('Not found address data.')]
            }}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return Response({
            "place": place,
        }, status=status.HTTP_200_OK)
