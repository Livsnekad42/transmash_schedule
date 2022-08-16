from django.urls import path, include
from rest_framework.routers import DefaultRouter

from administration.views import GroupViewSet, PermissionAPIView, AdminUserAPIView, CompanyPlanViewSet, PartnerViewSet, \
    UserPlanViewSet

router = DefaultRouter(trailing_slash=True)
router.register(r'groups', GroupViewSet)
router.register(r'permissions', PermissionAPIView)
router.register(r'managers', AdminUserAPIView)
router.register(r'tariffs/user', UserPlanViewSet)
router.register(r'tariffs/company', CompanyPlanViewSet)
router.register(r'partners', PartnerViewSet)


urlpatterns = [
    path(r'', include(router.urls)),
]
