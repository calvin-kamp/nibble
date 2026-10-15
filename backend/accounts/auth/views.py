from django.conf import settings
from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
)

from .serializers import (
    AccountDeleteSerializer,
    LoginSerializer,
    PasswordChangeSerializer,
    RegisterSerializer,
    UserSerializer,
)


def current_refresh_jti(request):
    """The jti of the session's refresh token, None if it's missing or invalid."""
    raw = request.COOKIES.get(settings.AUTH_COOKIE["NAME"])

    if not raw:
        return None

    try:
        return RefreshToken(raw)["jti"]
    except TokenError:
        return None


def end_sessions(user, keep_jti=None):
    """Blacklists every refresh token of the user, except the one to keep."""
    tokens = OutstandingToken.objects.filter(user=user, blacklistedtoken__isnull=True)

    if keep_jti:
        tokens = tokens.exclude(jti=keep_jti)

    BlacklistedToken.objects.bulk_create(
        [BlacklistedToken(token=token) for token in tokens], ignore_conflicts=True
    )


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        refresh_token = RefreshToken.for_user(user)

        response = Response(
            {
                "user": UserSerializer(user).data,
                "access": str(refresh_token.access_token),
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

        response.set_cookie(
            settings.AUTH_COOKIE["NAME"],
            value=str(refresh_token),
            max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
            secure=settings.AUTH_COOKIE["SECURE"],
            httponly=True,
            samesite=settings.AUTH_COOKIE["SAMESITE"],
            path=settings.AUTH_COOKIE["PATH"],
        )
        return response

    def perform_create(self, serializer):
        return serializer.save()


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e

        refresh_token = serializer.validated_data.pop("refresh")

        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        response.set_cookie(
            settings.AUTH_COOKIE["NAME"],
            value=str(refresh_token),
            max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
            secure=settings.AUTH_COOKIE["SECURE"],
            httponly=True,
            samesite=settings.AUTH_COOKIE["SAMESITE"],
            path=settings.AUTH_COOKIE["PATH"],
        )

        return response


class LogoutView(TokenBlacklistView):
    def post(self, request: Request, *args, **kwargs):
        cookie = {"refresh": request.COOKIES.get(settings.AUTH_COOKIE["NAME"])}
        response = Response(status=status.HTTP_204_NO_CONTENT)

        if not cookie["refresh"]:
            return response

        serializer = self.get_serializer(data=cookie)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            pass

        response.delete_cookie(
            settings.AUTH_COOKIE["NAME"],
            path=settings.AUTH_COOKIE["PATH"],
        )

        return response


class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request: Request, *args, **kwargs):
        cookie = {"refresh": request.COOKIES.get(settings.AUTH_COOKIE["NAME"])}

        if not cookie["refresh"]:
            raise InvalidToken("Kein Refresh-Token vorhanden.")

        serializer = self.get_serializer(data=cookie)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e

        refresh_token = serializer.validated_data.pop("refresh")

        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        response.set_cookie(
            settings.AUTH_COOKIE["NAME"],
            value=str(refresh_token),
            max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
            secure=settings.AUTH_COOKIE["SECURE"],
            httponly=True,
            samesite=settings.AUTH_COOKIE["SAMESITE"],
            path=settings.AUTH_COOKIE["PATH"],
        )

        return response


class PasswordChangeView(generics.GenericAPIView):
    """POST /auth/password/ – the current session stays, all others end."""

    serializer_class = PasswordChangeSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        with transaction.atomic():
            user.set_password(serializer.validated_data["new_password"])
            user.save(update_fields=["password"])
            end_sessions(user, keep_jti=current_refresh_jti(request))

        return Response(status=status.HTTP_204_NO_CONTENT)


class AccountDeleteView(generics.GenericAPIView):
    """POST /auth/delete-account/ – deletes the account with all its data.

    The password confirms that the account holder deletes. Profile, body data,
    goals, diary, weight, own meals and own recipes go with the user (cascade);
    every session ends.
    """

    serializer_class = AccountDeleteSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        with transaction.atomic():
            end_sessions(user)

            # Cascading deletes skip the files; recipe images have to go too.
            for recipe in user.recipes.exclude(image=""):
                recipe.image.delete(save=False)

            user.delete()

        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(
            settings.AUTH_COOKIE["NAME"],
            path=settings.AUTH_COOKIE["PATH"],
        )

        return response
