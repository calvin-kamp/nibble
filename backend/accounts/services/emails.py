from django.conf import settings
from django.utils import timezone

from config.emails import send_email

from .tokens import (
    make_email_change_token,
    make_password_reset_token,
    make_verification_token,
)


def send_verification_email(user):
    link = f"{settings.FRONTEND_URL}/verify-email?token={make_verification_token(user)}"

    send_email(
        user.email,
        "Bitte bestätige deine E-Mail-Adresse",
        "Hallo,\n\n"
        "bitte bestätige deine E-Mail-Adresse über diesen Link:\n"
        f"{link}\n\n"
        "Der Link ist 3 Tage gültig.",
    )


def send_email_change_email(user, new_email):
    """The link goes to the new address; only the click there makes it the account's."""
    token = make_email_change_token(user, new_email)
    link = f"{settings.FRONTEND_URL}/email-aendern?token={token}"

    send_email(
        new_email,
        "Bitte bestätige deine neue E-Mail-Adresse",
        "Hallo,\n\n"
        "du möchtest diese Adresse für dein Nibble-Konto verwenden. Bestätige sie "
        "über diesen Link:\n"
        f"{link}\n\n"
        "Der Link ist 24 Stunden gültig. Bis dahin bleibt deine bisherige Adresse "
        "bestehen. Wenn du das nicht angefordert hast, kannst du diese E-Mail ignorieren.",
    )


def send_email_change_requested_email(user, new_email):
    """Notice to the current address, in case the request did not come from the user.
    Notification only, so unverified accounts get nothing."""
    if not user.email_verified:
        return

    send_email(
        user.email,
        "Deine E-Mail-Adresse soll geändert werden",
        "Hallo,\n\n"
        f"für dein Konto wurde gerade die neue E-Mail-Adresse {new_email} angegeben. "
        "Sie gilt erst, wenn der Link in der Bestätigungs-E-Mail an diese Adresse "
        "geöffnet wird.\n\n"
        "Wenn du das nicht warst, ändere bitte sofort dein Passwort.",
    )


def send_password_reset_email(user):
    link = f"{settings.FRONTEND_URL}/reset-password?token={make_password_reset_token(user)}"

    send_email(
        user.email,
        "Passwort zurücksetzen",
        "Hallo,\n\n"
        "über diesen Link kannst du ein neues Passwort setzen:\n"
        f"{link}\n\n"
        "Der Link ist 1 Stunde gültig. Wenn du das nicht angefordert hast, "
        "kannst du diese E-Mail ignorieren.",
    )


def send_password_changed_email(user):
    """Notification only, so unverified accounts get nothing."""
    if not user.email_verified:
        return

    send_email(
        user.email,
        "Dein Passwort wurde geändert",
        "Hallo,\n\n"
        "das Passwort deines Kontos wurde gerade geändert. Wenn du das nicht "
        "warst, setze dein Passwort bitte sofort über „Passwort vergessen“ zurück.",
    )


def send_deletion_scheduled_email(user):
    """Notification only, so unverified accounts get nothing."""
    if not user.email_verified:
        return

    deletion_date = timezone.localtime(user.deletion_scheduled_for)

    send_email(
        user.email,
        "Dein Konto wird gelöscht",
        "Hallo,\n\n"
        "du hast die Löschung deines Kontos beantragt. Am "
        f"{deletion_date:%d.%m.%Y um %H:%M} Uhr wird es endgültig gelöscht.\n\n"
        "Bis dahin kannst du die Löschung zurücknehmen, indem du dich anmeldest "
        "und sie abbrichst.",
    )
