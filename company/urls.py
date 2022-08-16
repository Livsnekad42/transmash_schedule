from django.urls import path, include
from rest_framework.routers import DefaultRouter

from company.views import CompanyViewSet, BranchViewSet, RoleCompanyViewSet, ManagerCompanyViewSet, \
    CompanyDataFromInnApiView

router = DefaultRouter(trailing_slash=True)
router.register(r'profile', CompanyViewSet)
router.register(r'branch', BranchViewSet)
router.register(r'roles', RoleCompanyViewSet)
router.register(r'managers', ManagerCompanyViewSet)


urlpatterns = [
    path(r'', include(router.urls)),
    path(r'inn/', CompanyDataFromInnApiView.as_view(), name="inn")
]
