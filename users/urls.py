from django.urls import path
from .views import (
    CustomLoginView,
    CommonUserRegisterView,
    UserProfileView,
    LogoutView,
    WalletAddressView
)
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView


urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="rest_login"),
    path("register/common/", CommonUserRegisterView.as_view(), name="common_register"),
    path("password/reset/", PasswordResetView.as_view(), name="password_reset"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("logout/", LogoutView.as_view(), name="rest_logout"),
    path("password/reset/confirm", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('wallet/', WalletAddressView.as_view(), name='user-wallet'),
]
