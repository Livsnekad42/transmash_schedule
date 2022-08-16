from typing import Dict, Callable

from django.db import models
from rest_framework.filters import BaseFilterBackend


class BaseFilterAPI(BaseFilterBackend):
    filter_keys = {}
    custom_filter: Dict[str, Callable[[models.query.QuerySet, str],  models.query.QuerySet]] = {}

    def filter_queryset(self, request, queryset, view):
        query_params = request.query_params

        _filter = {}
        for filter_key in self.filter_keys:
            query_param = query_params.get(filter_key)
            if query_param:
                _filter[self.filter_keys[filter_key]] = query_param

        queryset = queryset.filter(**_filter)

        for filter_custom_key in self.custom_filter:
            query_param = query_params.get(filter_custom_key)
            if query_param:
                queryset = self.custom_filter[filter_custom_key](queryset, query_param)

        return queryset

    def get_schema_operation_parameters(self, view):
        query_filters = list(map(lambda field: {
            "name": field,
            "in": "query",
            "required": False,
            "description": field,
            "schema": {"type": "string"}
        }, {**self.filter_keys, **self.custom_filter}))
        return query_filters
