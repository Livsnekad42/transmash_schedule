from django.urls import path, include
from rest_framework.routers import DefaultRouter

from profiles.views import ProfileViewSet, RefreshPasswordApiView, RefreshEmailApiView

urlpatterns = [
    path(r'user/', ProfileViewSet.as_view()),
    path('refresh-pass/', RefreshPasswordApiView.as_view(), name='refresh_pass'),
    path('refresh-email/', RefreshEmailApiView.as_view(), name='refresh_email'),
]
