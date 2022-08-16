import httpx
from asgiref.sync import async_to_sync
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework import mixins, viewsets, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from company.filters import ManagerFilterBackend, CompanyFilterBackend
from company.models import Company, Branch, Role, Manager
from company.permissions import ManagerCompanyPermission, ManagerRoleCompanyPermission
from company.serializers import CompanySerializer, BranchSerializer, RoleSerializer, ManagerSerializer, \
    PublicCompanySerializer, CompanyINNSerializer
from company.services.company_data_inn import get_company_data_from_inn
from core.permissions.manager import get_company_from_request
from core.utils import get_profile_in_request
from profiles.models import TypeUser


class CompanyDataFromInnApiView(GenericAPIView):
    permission_classes = (ManagerCompanyPermission,)
    serializer_class = CompanyINNSerializer

    @method_decorator(async_to_sync)
    async def post(self, request):
        inn = request.data.get("inn")

        if not inn:
            return Response({'errors': {
                "detail": [_('Not provided INN.')]
            }}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        try:
            data = await get_company_data_from_inn(inn)
        except httpx.ConnectTimeout:
            return Response({'errors': {
                "detail": [_('Connect timeout.')]
            }}, status=status.HTTP_400_BAD_REQUEST)

        if not data:
            return Response({'errors': {
                "detail": [_('Not found company data.')]
            }}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return Response(data, status=status.HTTP_200_OK)


class CompanyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Company.objects.select_related('address', 'profile', )
    permission_classes = (ManagerCompanyPermission, )
    serializer_class = CompanySerializer

    def get_queryset(self):
        queryset = self.queryset
        return queryset

    def list(self, request, *args, **kwargs):
        company = get_company_from_request(request)

        self.check_object_permissions(request, company)

        serializer = self.serializer_class(
            company,
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        profile = get_profile_in_request(request)
        company = getattr(profile, "company", None)

        if company:
            return Response({'errors': {
                "detail": [_('The user already has a company.')]
            }}, status=status.HTTP_401_UNAUTHORIZED)

        manager = getattr(profile, "manager", None)
        if manager:
            return Response({'errors': {
                "detail": [_('Unable to link a company to this account.')]
            }}, status=status.HTTP_401_UNAUTHORIZED)

        if profile.user_type == TypeUser.MANAGER.value or profile.user_type == TypeUser.ADMIN.value:
            return Response({'errors': {
                "detail": [_('Admin can\'t create own company.')]
            }}, status=status.HTTP_401_UNAUTHORIZED)

        serializer_data = request.data
        serializer_context = {'profile': profile}
        serializer = self.serializer_class(
            data=serializer_data,
            context=serializer_context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        company = get_company_from_request(request)
        self.check_object_permissions(request, company)

        serializer_data = request.data
        serializer = self.serializer_class(
            company,
            data=serializer_data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        profile = get_profile_in_request(request)
        company = getattr(profile, "company", None)

        if not company:
            return Response({'errors': {
                "detail": [_('Access is denied.')]
            }}, status=status.HTTP_401_UNAUTHORIZED)

        if company.organizational_legal_form:
            company.organizational_legal_form.delete()

        if company.bank_details:
            company.bank_details.delete()

        company.delete()
        profile.user_type = TypeUser.USER.value
        profile.save()
        return Response({}, status=status.HTTP_200_OK)


class BranchViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Branch.objects.all()
    permission_classes = (ManagerCompanyPermission,)
    serializer_class = BranchSerializer

    def get_queryset(self):
        queryset = self.queryset.select_related('address', 'company', 'company__profile', )
        return queryset

    def retrieve(self, request, pk):
        company = get_company_from_request(request)
        self.check_object_permissions(request, company)
        try:
            branch = self.get_queryset().filter(company__pk=company.pk).filter(pk=pk).get()

        except Branch.DoesNotExist:
            return Response({'errors': {
                "detail": [_('Not found or permission denied.')]
            }}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.serializer_class(
            branch,
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        company = get_company_from_request(request)

        self.check_object_permissions(request, company)

        serializer_context = {'company': company}

        serializer_data = request.data
        serializer_data["company"] = company.pk

        serializer = self.serializer_class(
            data=serializer_data,
            context=serializer_context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        company = get_company_from_request(request)
        self.check_object_permissions(request, company)
        branches = self.get_queryset().filter(company__pk=company.pk)

        page = self.paginate_queryset(branches)
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)

    def update(self, request, pk):
        company = get_company_from_request(request)
        self.check_object_permissions(request, company)
        serializer_data = request.data

        try:
            branch = self.get_queryset().filter(company__pk=company.pk, pk=pk).get()

        except Branch.DoesNotExist:
            return Response({'errors': {
                "detail": [_('Not found or permission denied.')]
            }}, status=status.HTTP_401_UNAUTHORIZED)

        serializer_data["company"] = company.pk

        serializer = self.serializer_class(
            branch,
            data=serializer_data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        company = get_company_from_request(request)
        self.check_object_permissions(request, company)
        try:
            branch = self.get_queryset().filter(company__pk=company.pk).filter(pk=pk).get()

        except Branch.DoesNotExist:
            return Response({'errors': {
                "detail": [_('Not found or permission denied.')]
            }}, status=status.HTTP_401_UNAUTHORIZED)

        branch.delete()
        return Response({}, status=status.HTTP_200_OK)


class RoleCompanyViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Role.objects.select_related('company', 'company__profile', 'branch', 'branch__company',
                                           'branch__company__profile')
    permission_classes = (ManagerRoleCompanyPermission,)
    serializer_class = RoleSerializer

    def get_queryset(self):
        queryset = self.queryset
        return queryset

    def retrieve(self, request, pk):
        company = get_company_from_request(request)
        self.check_object_permissions(request, company)
        try:
            role = self.get_queryset().filter(company__pk=company.pk).filter(pk=pk).get()

        except Role.DoesNotExist:
            return Response({'errors': {
                "detail": [_('Not found or permission denied.')]
            }}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.serializer_class(
            role,
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        company = get_company_from_request(request)
        self.check_object_permissions(request, company)

        serializer_context = {'company': company}

        serializer_data = request.data
        serializer_data["company"] = company.pk

        serializer = self.serializer_class(
            data=serializer_data,
            context=serializer_context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        company = get_company_from_request(request)
        self.check_object_permissions(request, company)
        roles = self.get_queryset().filter(company__pk=company.pk)

        page = self.paginate_queryset(roles)
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)

    def destroy(self, request, pk):
        company = get_company_from_request(request)
        self.check_object_permissions(request, company)
        try:
            role = self.get_queryset().filter(company__pk=company.pk).filter(pk=pk).get()

        except Role.DoesNotExist:
            return Response({'errors': {
                "detail": [_('Not found or permission denied.')]
            }}, status=status.HTTP_401_UNAUTHORIZED)

        role.delete()
        return Response({}, status=status.HTTP_200_OK)

    def update(self, request, pk):
        company = get_company_from_request(request)
        self.check_object_permissions(request, company)
        try:
            role = self.get_queryset().filter(company__pk=company.pk).filter(pk=pk).get()

        except Role.DoesNotExist:
            return Response({'errors': {
                "detail": [_('Not found or permission denied.')]
            }}, status=status.HTTP_401_UNAUTHORIZED)

        serializer_data = request.data
        serializer_data["company"] = company.pk

        serializer = self.serializer_class(
            role,
            data=serializer_data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ManagerCompanyViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Manager.objects.all()
    permission_classes = (ManagerRoleCompanyPermission,)
    serializer_class = ManagerSerializer
    filter_backends = (ManagerFilterBackend,)

    def get_queryset(self):
        queryset = self.queryset.select_related('profile', 'company', 'company__profile', ).prefetch_related('roles',)
        return queryset

    def retrieve(self, request, pk):
        company = get_company_from_request(request)
        self.check_object_permissions(request, company)
        try:
            manager = self.get_queryset().filter(company__pk=company.pk).filter(pk=pk).get()

        except Manager.DoesNotExist:
            return Response({'errors': {
                "detail": [_('Not found or permission denied.')]
            }}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.serializer_class(
            manager,
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        company = get_company_from_request(request)
        self.check_object_permissions(request, company)
        serializer_context = {'company': company}

        serializer_data = request.data
        serializer_data["company"] = company.pk

        serializer = self.serializer_class(
            data=serializer_data,
            context=serializer_context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        company = get_company_from_request(request)
        self.check_object_permissions(request, company)

        managers = self.filter_queryset(self.get_queryset().filter(company__pk=company.pk))
        page = self.paginate_queryset(managers)
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)

    def update(self, request, pk):
        company = get_company_from_request(request)
        self.check_object_permissions(request, company)
        try:
            manager = self.get_queryset().filter(company__pk=company.pk, pk=pk).get()

        except Manager.DoesNotExist:
            return Response({'errors': {
                "detail": [_('Not found or permission denied.')]
            }}, status=status.HTTP_401_UNAUTHORIZED)

        serializer_data = request.data
        serializer_data["company"] = company.pk

        serializer = self.serializer_class(
            manager,
            data=serializer_data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        company = get_company_from_request(request)
        self.check_object_permissions(request, company)
        try:
            manager = self.get_queryset().filter(company__pk=company.pk, pk=pk).get()

        except Manager.DoesNotExist:
            return Response({'errors': {
                "detail": [_('Not found or permission denied.')]
            }}, status=status.HTTP_401_UNAUTHORIZED)

        manager.delete()
        return Response({}, status=status.HTTP_200_OK)


class PublicCompanyViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Company.objects.select_related('address',)
    permission_classes = (AllowAny, )
    serializer_class = PublicCompanySerializer
    filter_backends = (CompanyFilterBackend, )

    def get_queryset(self):
        queryset = self.queryset.select_related('address',)
        return queryset

    def list(self, request, *args, **kwargs):
        companies = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(companies)
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)


