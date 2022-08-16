from django.db.models import Q

from core.filters import BaseFilterAPI


class CompanyFilterBackend(BaseFilterAPI):
    filter_keys = {
        "name": "name__icontains",
        "city": "address__street__city__name__icontains",
        "street": "address__street__street__icontains",
    }


class ManagerFilterBackend(BaseFilterAPI):
    filter_keys = {
        "query": True,
    }

    def filter_queryset(self, request, queryset, view):
        query_params = request.query_params
        query = query_params.get("query")

        if query:
            queryset = queryset.filter(
                Q(profile__user__email__icontains=query) |
                Q(profile__first_name__icontains=query) |
                Q(profile__last_name__icontains=query)
            )

        return queryset
