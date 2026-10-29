from rest_framework import status

from config.exceptions import ApiError, Conflict


class EmailTaken(Conflict):
    default_code = "email_taken"
    default_detail = "Diese E-Mail-Adresse ist bereits registriert."


class UsernameTaken(Conflict):
    default_code = "username_taken"
    default_detail = "Dieser Username ist bereits vergeben."


class InvalidCredentials(ApiError):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_code = "invalid_credentials"
    default_detail = "E-Mail-Adresse oder Passwort ist falsch."


class InvalidLinkToken(ApiError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "invalid_token"
    default_detail = "Der Link ist ungültig oder abgelaufen."


class AlreadyVerified(ApiError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "already_verified"
    default_detail = "Deine E-Mail-Adresse ist bereits bestätigt."


class OnboardingStepNotAllowed(ApiError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "onboarding_step_not_allowed"
    default_detail = "Dieser Schritt ist gerade nicht möglich."
