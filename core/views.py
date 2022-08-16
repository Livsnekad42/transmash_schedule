from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ViewSetMixin

CACHE_TTL = getattr(settings, "CACHE_TTL", 60)


class CacheApiView(GenericAPIView):
    @method_decorator(cache_page(CACHE_TTL))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CacheGenericViewSet(ViewSetMixin, CacheApiView):
    pass
