from django.urls import path, include
from rest_framework.routers import DefaultRouter

from employee.views import EmployeeViewSet

router = DefaultRouter(trailing_slash=True)

router.register(r'employee', EmployeeViewSet)


urlpatterns = [
    path(r'', include(router.urls)),
]