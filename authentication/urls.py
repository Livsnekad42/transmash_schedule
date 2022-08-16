from django.urls import path

from authentication.views import (
    RegistrationAPIView,
    VerificationAPIView,
    Login,
    LogoutApiView,
    TokenAuthApiView,
    RestorePasswordApiView,
    ConfirmRestorePasswordApiView,
)

urlpatterns = [
    path('registration/', RegistrationAPIView.as_view(), name="registration_email"),
    path('verification/', VerificationAPIView.as_view(), name="verification_email"),
    path('login/', Login.as_view(), name="login"),
    path('logout/', LogoutApiView.as_view(), name='logout'),
    path('refresh-token/', TokenAuthApiView.as_view(), name='refresh_token'),
    path('restore-pass/', RestorePasswordApiView.as_view(), name='restore_pass'),
    path('confirm-code/', ConfirmRestorePasswordApiView.as_view(), name='confirm_code'),
]
