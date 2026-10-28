from django.urls import path

from .views import (
    CsrfView,
    CurrentAccountView,
    EmailChangeConfirmView,
    EmailChangeView,
    EmailVerificationResendView,
    EmailVerifyView,
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordForgotView,
    PasswordResetView,
    RefreshView,
    RegisterView,
)

urlpatterns = [
    path("csrf", CsrfView.as_view(), name="csrf"),
    path("register", RegisterView.as_view(), name="register"),
    path("login", LoginView.as_view(), name="login"),
    path("refresh", RefreshView.as_view(), name="token_refresh"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("me", CurrentAccountView.as_view(), name="current_account"),
    path("email/verify", EmailVerifyView.as_view(), name="email_verify"),
    path(
        "email/verification/resend",
        EmailVerificationResendView.as_view(),
        name="email_verification_resend",
    ),
    path("email/change", EmailChangeView.as_view(), name="email_change"),
    path(
        "email/change/confirm",
        EmailChangeConfirmView.as_view(),
        name="email_change_confirm",
    ),
    path("password/change", PasswordChangeView.as_view(), name="password_change"),
    path("password/forgot", PasswordForgotView.as_view(), name="password_forgot"),
    path("password/reset", PasswordResetView.as_view(), name="password_reset"),
]
