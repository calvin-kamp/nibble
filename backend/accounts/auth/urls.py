from django.urls import path

from .views import (
    AccountDeleteView,
    CookieTokenRefreshView,
    CurrentUserView,
    LoginView,
    LogoutView,
    PasswordChangeView,
    RegisterView,
)

urlpatterns = [
    path("me/", CurrentUserView.as_view(), name="current_user"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password/", PasswordChangeView.as_view(), name="password_change"),
    path("delete-account/", AccountDeleteView.as_view(), name="account_delete"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
]
