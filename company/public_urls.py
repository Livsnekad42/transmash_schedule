from django.urls import path, include
from rest_framework.routers import DefaultRouter

from company.views import PublicCompanyViewSet

router = DefaultRouter(trailing_slash=True)
router.register(r'companies', PublicCompanyViewSet)


urlpatterns = [
    path(r'', include(router.urls)),
]