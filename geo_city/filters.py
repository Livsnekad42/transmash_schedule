import operator
from functools import reduce

from django.db.models import Q
from rest_framework.filters import BaseFilterBackend


class SearchFilterCityBackend(BaseFilterBackend):
    filter_keys = {
        "region": "region__name__icontains",
        "city": "name__icontains",
        "latitude": "latitude__icontains",
        "longitude": "longitude__icontains",
    }

    to_capitalize = {
        "region",
        "city",
    }

    def filter_queryset(self, request, queryset, view):
        query_params = request.query_params
        filter = {}

        for filter_key in self.filter_keys:
            query_param = query_params.get(filter_key)
            if query_param:
                filter[self.filter_keys[filter_key]] = query_param.capitalize() if filter_key in self.to_capitalize else query_param

        queryset = queryset.filter(**filter)

        return queryset

    def get_schema_operation_parameters(self, view):
        query_filters = list(map(lambda field: {
            "name": field,
            "in": "query",
            "required": False,
            "description": field,
            "schema": {"type": "string"}
        }, self.filter_keys))

        return query_filters


class SearchFilterStreetBackend(BaseFilterBackend):
    filter_keys = {
        "query": "query",
    }

    to_capitalize = {
        "city",
        "street",
    }

    def filter_queryset(self, request, queryset, view):
        query_params = request.query_params
        query = query_params.get("query")

        if query:
            # TODO: когда переедем на postgres убрать title
            query = query.title()
            queryes = list(map(lambda s: s.strip(), query.split(" ")))
            if len(queryes) == 0:
                return queryset

            filters = reduce(
                operator.or_,
                [
                    Q(street__street__icontains=_q) for _q in queryes[1:]
                ],
                Q()
            )

            queryset = queryset.filter(city__name__icontains=queryes[0]).filter(filters)

        return queryset

    def get_schema_operation_parameters(self, view):
        query_filters = list(map(lambda field: {
            "name": field,
            "in": "query",
            "required": False,
            "description": field,
            "schema": {"type": "string"}
        }, self.filter_keys))
        return query_filters


class SearchFilterPlaceBackend(BaseFilterBackend):
    filter_keys = {
        "query": "query",
    }

    def filter_queryset(self, request, queryset, view):
        query_params = request.query_params
        query = query_params.get("query")

        if query:
            # TODO: когда переедем на postgres убрать title
            query = query.title()
            queryes = list(map(lambda s: s.strip(), query.split(" ")))
            if len(queryes) == 0:
                return queryset

            filters = reduce(
                operator.or_,
                [
                    Q(place_name__icontains=_q) |
                    Q(street__street__icontains=_q) for _q in queryes[1:]
                ],
                Q()
            )

            queryset = queryset.filter(city__name__icontains=queryes[0]).filter(filters)

        return queryset

    def get_schema_operation_parameters(self, view):
        query_filters = list(map(lambda field: {
            "name": field,
            "in": "query",
            "required": False,
            "description": field,
            "schema": {"type": "string"}
        }, self.filter_keys))
        return query_filters


class SearchFilterAddressBackend(BaseFilterBackend):
    filter_keys = {
        "query": "query",
    }

    def filter_queryset(self, request, queryset, view):
        query_params = request.query_params
        query = query_params.get("query")

        if query:
            # TODO: когда переедем на postgres убрать title
            query = query.title()
            queryes = list(map(lambda s: s.strip(), query.split(" ")))
            if len(queryes) == 0:
                return queryset

            filters = reduce(
                operator.or_,
                [
                    Q(home__icontains=_q) |
                    Q(street__street__icontains=_q) for _q in queryes[1:]
                ],
                Q()
            )

            queryset = queryset.filter(street__city__name__icontains=queryes[0]).filter(filters)

        return queryset

    def get_schema_operation_parameters(self, view):
        query_filters = list(map(lambda field: {
            "name": field,
            "in": "query",
            "required": False,
            "description": field,
            "schema": {"type": "string"}
        }, self.filter_keys))
        return query_filters
