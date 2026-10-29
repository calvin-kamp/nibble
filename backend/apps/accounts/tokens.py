from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core import signing
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)

from apps.accounts.models import User

VERIFICATION_SALT = "accounts.email-verification"
EMAIL_CHANGE_SALT = "accounts.email-change"


def make_verification_token(user):
    """Signed user id and address, so a changed address invalidates old links."""
    return signing.dumps(
        {"user": user.pk, "email": user.email},
        salt=VERIFICATION_SALT,
    )


def user_from_verification_token(token):
    try:
        data = signing.loads(
            token,
            salt=VERIFICATION_SALT,
            max_age=settings.EMAIL_VERIFICATION_MAX_AGE,
        )
    except signing.BadSignature:
        return None

    return User.objects.filter(
        pk=data.get("user"),
        email=data.get("email"),
        is_active=True,
    ).first()


def make_email_change_token(user, new_email):
    """Signed user id, current and new address. Nothing is stored until the click, and
    the link dies once the current address has changed."""
    return signing.dumps(
        {"user": user.pk, "email": user.email, "new_email": new_email},
        salt=EMAIL_CHANGE_SALT,
    )


def email_change_from_token(token):
    """(user, new address) from a valid link, otherwise (None, None).

    A user who already has the new address is returned too, so a second click on the
    same link still counts as done.
    """
    try:
        data = signing.loads(
            token,
            salt=EMAIL_CHANGE_SALT,
            max_age=settings.EMAIL_CHANGE_MAX_AGE,
        )
    except signing.BadSignature:
        return None, None

    new_email = data.get("new_email")
    user = User.objects.filter(
        pk=data.get("user"),
        email__in=[data.get("email"), new_email],
        is_active=True,
    ).first()

    return (user, new_email) if user else (None, None)


def make_password_reset_token(user):
    """User id plus Django's reset token, which dies with the next password change."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    return f"{uid}.{default_token_generator.make_token(user)}"


def user_from_password_reset_token(token):
    uid, _, user_token = token.partition(".")

    try:
        pk = force_str(urlsafe_base64_decode(uid))
    except (TypeError, ValueError):
        return None

    if not pk.isdigit():
        return None

    user = User.objects.filter(pk=pk, is_active=True).first()

    if user is None or not default_token_generator.check_token(user, user_token):
        return None

    return user


def blacklist_user_tokens(user):
    """Blocks every refresh token of the user, e.g. after a password change."""
    tokens = OutstandingToken.objects.filter(user=user, blacklistedtoken__isnull=True)

    BlacklistedToken.objects.bulk_create(
        [BlacklistedToken(token=token) for token in tokens],
        ignore_conflicts=True,
    )
