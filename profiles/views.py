from django.utils.translation import gettext_lazy as _

from rest_framework import generics, mixins, status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import (
    AllowAny, IsAuthenticated
)
from rest_framework.response import Response

from authentication.models import User
from profiles.models import Profile
from profiles.serializers import ProfileSerializer, RefreshPasswordSerializer, RefreshEmailSerializer


class RefreshPasswordApiView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RefreshPasswordSerializer

    def post(self, request):
        data = request.data
        user = request.user

        serializer = self.serializer_class(user, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class RefreshEmailApiView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RefreshEmailSerializer

    def post(self, request):
        user = request.data
        try:
            user_db = User.model_objects.get(email=user["email"])

        except (User.DoesNotExist, KeyError):
            return Response({'email': [_('Invalid email.')]}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(user_db, data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileViewSet(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer
    pagination_class = None

    def get(self, request, *args, **kwargs):
        user_id = request.user.pk

        try:
            serializer_instance = Profile.objects.filter(user__id=user_id).get()
        except Profile.DoesNotExist:
            raise NotFound(_('Permission denied'))

        serializer = self.serializer_class(
            serializer_instance
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        user_id = request.user.pk

        try:
            serializer_instance = Profile.objects.filter(user__id=user_id).get()
        except Profile.DoesNotExist:
            raise NotFound(_('Permission denied'))

        serializer_data = request.data

        serializer = self.serializer_class(
            serializer_instance,
            data=serializer_data,
            context=request.FILES,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
