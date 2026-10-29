from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


def set_auth_cookies(response, user):
    """Issues a fresh token pair for the user and stores it in HttpOnly cookies."""
    cookie = settings.AUTH_COOKIE
    refresh_token = RefreshToken.for_user(user)
    options = {
        "domain": cookie["DOMAIN"],
        "secure": cookie["SECURE"],
        "httponly": True,
        "samesite": cookie["SAMESITE"],
    }

    response.set_cookie(
        cookie["ACCESS_NAME"],
        value=str(refresh_token.access_token),
        max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
        path=cookie["ACCESS_PATH"],
        **options,
    )
    response.set_cookie(
        cookie["REFRESH_NAME"],
        value=str(refresh_token),
        max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
        path=cookie["REFRESH_PATH"],
        **options,
    )

    return response


def delete_auth_cookies(response):
    cookie = settings.AUTH_COOKIE

    for name, path in (
        (cookie["ACCESS_NAME"], cookie["ACCESS_PATH"]),
        (cookie["REFRESH_NAME"], cookie["REFRESH_PATH"]),
    ):
        response.delete_cookie(
            name,
            path=path,
            domain=cookie["DOMAIN"],
            samesite=cookie["SAMESITE"],
        )

    return response
