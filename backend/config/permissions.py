from rest_framework.permissions import IsAdminUser


class IsStaff(IsAdminUser):
    """Staff endpoints of every app, mounted under /moderation/; is_staff decides.

    One name for all of them, so a later role check changes one place.
    """
