from datetime import datetime, timedelta
from typing import Union

from django.contrib.auth import login, logout
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from rest_framework.generics import GenericAPIView

from rest_framework_jwt.settings import api_settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

from .models import User
from .serializers import RegistrationSerializer, VerifyUserSerializer, LoginSerializer, RefreshTokenSerializer, \
    RestorePasswordSerializer, ConfirmRestorePasswordSerializer
from .services.converter import phone_converter


# Максимальное количество неудачных попыток войти в свой профиль
COUNT_FAILED_ATTEMPT = getattr(settings, "COUNT_FAILED_ATTEMPT", 2)
# Время бана пользователя при исчерпании всех доступных попыток
BAN_TIME = getattr(settings, "BAN_TIME", timedelta(minutes=30))
# COOKIE REFRESH KEY
COOKIE_REFRESH_TOKEN_KEY = getattr(settings, "COOKIE_REFRESH_TOKEN_KEY", "refresh_token")


class RegistrationAPIView(GenericAPIView):
    '''
    post:
        Регистрация по email и password
     '''
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer_data = request.data
        serializer = self.serializer_class(data=serializer_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VerificationAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = VerifyUserSerializer

    def post(self, request):
        user = request.data

        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = Response(serializer.data, status=status.HTTP_200_OK)
        refresh_token = serializer.data.get("refresh_token")
        if refresh_token:
            expiration = (datetime.utcnow() + api_settings.JWT_REFRESH_EXPIRATION_DELTA)
            response.set_cookie(COOKIE_REFRESH_TOKEN_KEY,
                                refresh_token,
                                expires=expiration,
                                httponly=True)
        return response


class Login(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.data.get("refresh_token")
        if not refresh_token:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        response = Response(serializer.data, status=status.HTTP_200_OK)
        expiration = (datetime.utcnow() + api_settings.JWT_REFRESH_EXPIRATION_DELTA)
        response.set_cookie(COOKIE_REFRESH_TOKEN_KEY,
                            refresh_token,
                            expires=expiration,
                            httponly=True)

        return response
        
    
class LogoutApiView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        response = Response({}, status=status.HTTP_200_OK)
        response.delete_cookie(COOKIE_REFRESH_TOKEN_KEY)
        return response


class TokenAuthApiView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RefreshTokenSerializer
    
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(COOKIE_REFRESH_TOKEN_KEY)
        if not refresh_token:
            refresh_token = request.data.get("refresh_token")

        serializer = self.serializer_class(data={"refresh_token": refresh_token})
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.data.get("refresh_token")
        response = Response(serializer.data, status=status.HTTP_200_OK)
        expiration = (datetime.utcnow() + api_settings.JWT_REFRESH_EXPIRATION_DELTA)
        response.set_cookie(COOKIE_REFRESH_TOKEN_KEY,
                            refresh_token,
                            expires=expiration,
                            httponly=True)

        return response


class RestorePasswordApiView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RestorePasswordSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        return Response({}, status=status.HTTP_200_OK)


class ConfirmRestorePasswordApiView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ConfirmRestorePasswordSerializer

    def post(self, request):
        serializer_data = request.data
        serializer = self.serializer_class(data=serializer_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
