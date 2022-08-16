import operator
from functools import reduce

from django.contrib.auth.models import Group, Permission
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from rest_framework import mixins, viewsets, status
from rest_framework.response import Response

from administration.models import Partner, CompanyPlan, UserPlan
from administration.permissions import IsAdminAdmin
from administration.serializers import GroupSerializer, PermissionModuleSerializer, PermissionSerializer, \
    AdminProfileSerializer, PartnerSerializer, CompanyPlanSerializer, UserPlanSerializer
from administration.services.constants import ADMIN_MODULES
from profiles.models import Profile


class GroupViewSet(viewsets.ModelViewSet):
    """
    Методы для создания групп пользователей с разными доступами
    """
    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    permission_classes = (IsAdminAdmin, )


class PermissionAPIView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    Список доступов разбитый по модулям
    """
    queryset = Permission.objects.all()
    permission_classes = (IsAdminAdmin, )
    serializer_class = PermissionModuleSerializer

    def list(self, request, *args, **kwargs):
        permissions = Permission.objects.filter(
            reduce(
                operator.or_,
                (Q(codename__contains=item["model"].model_name()) for item in ADMIN_MODULES)
            )
        )

        data = []
        for _module in ADMIN_MODULES:
            _permissions = []
            for _perm in permissions:
                if _module["model"].model_name() == _perm.content_type.model:
                    permissions.append(
                        PermissionSerializer(_perm).data
                    )

            data.append({
                "module": _module["title"],
                "permissions": _permissions,
            })

        return Response(data, status=status.HTTP_200_OK)


class AdminUserAPIView(viewsets.ModelViewSet):
    """
    Методы создания административных менеджеров
    """
    queryset = Profile.objects.all()
    permission_classes = (IsAdminAdmin,)
    serializer_class = AdminProfileSerializer
    http_method_names = ['get', 'post', 'put']

    def get_queryset(self):
        queryset = self.queryset.select_related('user', )
        return queryset

    def destroy(self, request, pk):
        try:
            profile = self.get_queryset().filter(pk=pk).get()

        except Profile.DoesNotExist:
            return Response({'errors': {
                "detail": [_('Not found or permission denied.')]
            }}, status=status.HTTP_401_UNAUTHORIZED)

        family_nodes = profile.ref_family_nodes.all()
        if len(family_nodes) > 0:
            FamilyNode.objects.filter(pk__in=list(map(lambda f: f.pk, family_nodes))).delete()

        profile.delete()
        return Response({}, status=status.HTTP_200_OK)


class PartnerViewSet(viewsets.ModelViewSet):
    serializer_class = PartnerSerializer
    permission_classes = (IsAdminAdmin,)
    queryset = Partner.objects.all()


class CompanyPlanViewSet(viewsets.ModelViewSet):
    """
    Тарифные планы для компаний
    """
    serializer_class = CompanyPlanSerializer
    permission_classes = (IsAdminAdmin,)
    queryset = CompanyPlan.objects.all()

    def destroy(self, request, pk):
        try:
            plan = self.get_queryset().filter(pk=pk).get()

        except CompanyPlan.DoesNotExist:
            return Response({'errors': {
                "detail": [_('Not found or permission denied.')]
            }}, status=status.HTTP_401_UNAUTHORIZED)

        plan.is_archive = True
        plan.save()
        return Response({}, status=status.HTTP_200_OK)


class UserPlanViewSet(viewsets.ModelViewSet):
    """
    Тарифные планы для пользователей
    """
    serializer_class = UserPlanSerializer
    permission_classes = (IsAdminAdmin,)
    queryset = UserPlan.objects.all()

    def destroy(self, request, pk):
        try:
            plan = self.get_queryset().filter(pk=pk).get()

        except UserPlan.DoesNotExist:
            return Response({'errors': {
                "detail": [_('Not found or permission denied.')]
            }}, status=status.HTTP_401_UNAUTHORIZED)

        plan.is_archive = True
        plan.save()
        return Response({}, status=status.HTTP_200_OK)
