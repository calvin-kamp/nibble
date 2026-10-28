from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.db import IntegrityError
from django.middleware.csrf import get_token
from rest_framework import generics, status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.exceptions import (
    AlreadyVerified,
    EmailTaken,
    InvalidCredentials,
    InvalidLinkToken,
)
from accounts.models import User
from accounts.services.emails import (
    send_email_change_email,
    send_email_change_requested_email,
    send_password_changed_email,
    send_password_reset_email,
    send_verification_email,
)
from accounts.services.tokens import (
    blacklist_user_tokens,
    email_change_from_token,
    user_from_password_reset_token,
    user_from_verification_token,
)
from accounts.utils import delete_auth_cookies, set_auth_cookies

from .serializers import (
    AccountStateSerializer,
    EmailChangeSerializer,
    LoginSerializer,
    PasswordChangeSerializer,
    PasswordForgotSerializer,
    PasswordResetSerializer,
    RegisterSerializer,
    TokenSerializer,
    validate_new_password,
)
from .throttles import (
    EmailChangeThrottle,
    LoginThrottle,
    PasswordChangeThrottle,
    PasswordForgotEmailThrottle,
    PasswordForgotIPThrottle,
    RefreshThrottle,
    RegisterThrottle,
    VerificationResendThrottle,
)


class CsrfView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # get_token() also makes the middleware set the csrftoken cookie.
        return Response({"csrf_token": get_token(request)})


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegisterThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        if User.objects.filter(email=email).exists():
            raise EmailTaken()

        try:
            user = User.objects.create_user(
                email, serializer.validated_data["password"]
            )
        except IntegrityError as exc:
            raise EmailTaken() from exc

        update_last_login(None, user)
        send_verification_email(user)

        response = Response(
            AccountStateSerializer(user).data, status=status.HTTP_201_CREATED
        )

        return set_auth_cookies(response, user)


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # A scheduled deletion stays; the frontend asks whether to cancel it.
        user = authenticate(
            request._request,
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        if user is None:
            raise InvalidCredentials()

        update_last_login(None, user)
        response = Response(AccountStateSerializer(user).data)

        return set_auth_cookies(response, user)


class RefreshView(APIView):
    """Rotates the refresh token: the old one is blacklisted, both cookies renewed."""

    permission_classes = [AllowAny]
    throttle_classes = [RefreshThrottle]

    def post(self, request):
        raw_token = request.COOKIES.get(settings.AUTH_COOKIE["REFRESH_NAME"])

        if not raw_token:
            raise NotAuthenticated()

        try:
            refresh_token = RefreshToken(raw_token)
        except TokenError as exc:
            raise NotAuthenticated() from exc

        user = User.objects.filter(
            pk=refresh_token.get(jwt_settings.USER_ID_CLAIM),
            is_active=True,
        ).first()

        if user is None:
            raise NotAuthenticated()

        refresh_token.blacklist()

        return set_auth_cookies(Response(status=status.HTTP_204_NO_CONTENT), user)


class LogoutView(APIView):
    """Works with an expired access token too, only the refresh cookie counts."""

    permission_classes = [AllowAny]

    def post(self, request):
        raw_token = request.COOKIES.get(settings.AUTH_COOKIE["REFRESH_NAME"])

        if raw_token:
            try:
                RefreshToken(raw_token).blacklist()
            except TokenError:
                pass

        return delete_auth_cookies(Response(status=status.HTTP_204_NO_CONTENT))


class CurrentAccountView(generics.RetrieveAPIView):
    serializer_class = AccountStateSerializer

    def get_object(self):
        return self.request.user


class EmailVerifyView(APIView):
    """No login needed, so the link also works in another browser."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = user_from_verification_token(serializer.validated_data["token"])

        if user is None:
            raise InvalidLinkToken()

        if not user.email_verified:
            user.email_verified = True
            user.save(update_fields=["email_verified"])

        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailVerificationResendView(APIView):
    throttle_classes = [VerificationResendThrottle]

    def post(self, request):
        if request.user.email_verified:
            raise AlreadyVerified()

        send_verification_email(request.user)

        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailChangeView(APIView):
    """Only sends the link; the address stays as it is until the click."""

    throttle_classes = [EmailChangeThrottle]

    def post(self, request):
        serializer = EmailChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        new_email = serializer.validated_data["email"]

        send_email_change_email(request.user, new_email)
        send_email_change_requested_email(request.user, new_email)

        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailChangeConfirmView(APIView):
    """No login needed, so the link also works in another browser."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, new_email = email_change_from_token(serializer.validated_data["token"])

        if user is None:
            raise InvalidLinkToken()

        if user.email == new_email:
            return Response(status=status.HTTP_204_NO_CONTENT)

        # Someone may have registered the address since the link was sent.
        if User.objects.filter(email=new_email).exists():
            raise EmailTaken()

        # Opening the link proves the new address, so it counts as verified.
        user.email = new_email
        user.email_verified = True

        try:
            user.save(update_fields=["email", "email_verified"])
        except IntegrityError as exc:
            raise EmailTaken() from exc

        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordChangeView(APIView):
    """Logs out every other session; the current one gets new cookies."""

    throttle_classes = [PasswordChangeThrottle]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        blacklist_user_tokens(user)
        send_password_changed_email(user)

        return set_auth_cookies(Response(status=status.HTTP_204_NO_CONTENT), user)


class PasswordForgotView(APIView):
    """Always 204, so nobody can find out which addresses are registered."""

    permission_classes = [AllowAny]
    throttle_classes = [PasswordForgotIPThrottle, PasswordForgotEmailThrottle]

    def post(self, request):
        serializer = PasswordForgotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(
            email=serializer.validated_data["email"], is_active=True
        ).first()

        if user is not None:
            send_password_reset_email(user)

        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = user_from_password_reset_token(serializer.validated_data["token"])

        if user is None:
            raise InvalidLinkToken()

        password = serializer.validated_data["new_password"]
        validate_new_password(password, user)

        user.set_password(password)
        user.save(update_fields=["password"])
        blacklist_user_tokens(user)

        return Response(status=status.HTTP_204_NO_CONTENT)
