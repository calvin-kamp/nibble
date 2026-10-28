import math

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import set_rollback

VALIDATION_ERROR = "validation_error"
FUTURE_DATE_NOT_ALLOWED = "future_date_not_allowed"

MESSAGES = {
    VALIDATION_ERROR: "Die Eingabe ist ungültig.",
    FUTURE_DATE_NOT_ALLOWED: "Das Datum darf nicht in der Zukunft liegen.",
    "not_authenticated": "Du bist nicht angemeldet oder deine Sitzung ist abgelaufen.",
    "forbidden": "Dafür fehlt dir die Berechtigung.",
    "not_found": "Nicht gefunden.",
    "method_not_allowed": "Diese Methode ist hier nicht erlaubt.",
    "throttled": "Zu viele Anfragen. Bitte warte kurz und versuche es dann erneut.",
}

# DRF's own codes, renamed to the ones the API documents.
CODE_ALIASES = {
    "authentication_failed": "not_authenticated",
    "permission_denied": "forbidden",
}


class ApiError(exceptions.APIException):
    """Error with a fixed code and German message, see the Error schema."""


class Conflict(ApiError):
    status_code = status.HTTP_409_CONFLICT


def exception_handler(exc, context):
    """Renders every error as {"code", "message", "errors"?}."""
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, DjangoPermissionDenied):
        exc = exceptions.PermissionDenied()

    if not isinstance(exc, exceptions.APIException):
        return None

    headers = {}

    if getattr(exc, "auth_header", None):
        headers["WWW-Authenticate"] = exc.auth_header

    if getattr(exc, "wait", None):
        headers["Retry-After"] = str(math.ceil(exc.wait))

    set_rollback()

    return Response(error_body(exc), status=exc.status_code, headers=headers)


def error_body(exc):
    if isinstance(exc, exceptions.ValidationError):
        codes = set(leaf_values(exc.get_codes()))
        code = (
            FUTURE_DATE_NOT_ALLOWED
            if FUTURE_DATE_NOT_ALLOWED in codes
            else VALIDATION_ERROR
        )

        return {
            "code": code,
            "message": MESSAGES[code],
            "errors": flatten_errors(exc.detail),
        }

    codes = exc.get_codes()
    code = codes if isinstance(codes, str) else exc.default_code
    code = CODE_ALIASES.get(code, code)

    return {"code": code, "message": error_message(exc, code)}


def error_message(exc, code):
    """Our own text for DRF's defaults, the given text for everything else."""
    detail = str(exc.detail)

    if detail == str(exc.default_detail) or isinstance(exc, exceptions.Throttled):
        return MESSAGES.get(code, detail)

    return detail


def flatten_errors(detail, prefix=""):
    """Turns nested DRF errors into {"ingredients.0.amount": ["..."]}."""
    if isinstance(detail, dict):
        items = detail.items()
    elif isinstance(detail, list) and any(
        isinstance(item, (dict, list)) for item in detail
    ):
        items = enumerate(detail)
    else:
        messages = detail if isinstance(detail, list) else [detail]

        return {prefix or "non_field_errors": [str(message) for message in messages]}

    errors = {}

    for key, value in items:
        # Valid items of a nested list show up as empty dicts.
        if not value:
            continue

        errors.update(flatten_errors(value, f"{prefix}.{key}" if prefix else str(key)))

    return errors


def leaf_values(data):
    if isinstance(data, dict):
        for value in data.values():
            yield from leaf_values(value)
    elif isinstance(data, list):
        for value in data:
            yield from leaf_values(value)
    else:
        yield data
