"""Delivery of recipe images.

Images of approved recipes are public. Images of recipes that are still under review, and the
images of pending changes, are only for the author and staff: the file names are built from ID
and title and so are easy to guess.
"""

from django.conf import settings
from django.http import Http404
from django.views.static import serve
from rest_framework.request import Request

from apps.accounts.authentication import CookieJWTAuthentication

from .models import Recipe, RecipeSubmission


def _user(request):
    """The signed-in user from the auth cookie, or None. Read-only, so no CSRF check."""
    try:
        result = CookieJWTAuthentication().authenticate(Request(request))
    except (
        Exception
    ):  # an invalid or expired token counts as anonymous, like in the API
        return None

    return result[0] if result else None


def _may_see(user, recipe):
    if recipe.status == Recipe.Status.APPROVED:
        return True

    if user is None:
        return False

    return user.is_staff or recipe.author_id == getattr(user.profile, "pk", None)


def recipe_media(request, path):
    recipe = Recipe.objects.filter(image=path).first()
    public = recipe is not None and recipe.status == Recipe.Status.APPROVED

    if not public:
        user = _user(request)

        if recipe is not None:
            allowed = _may_see(user, recipe)
        else:
            submission = (
                RecipeSubmission.objects.select_related("recipe")
                .filter(image=path)
                .first()
            )
            allowed = (
                submission is not None
                and user is not None
                and (user.is_staff or submission.recipe.author_id == user.profile.pk)
            )

        # 404 instead of 403: whether the file exists is nobody else's business
        if not allowed:
            raise Http404

    response = serve(request, path, document_root=settings.MEDIA_ROOT)

    if not public:
        response["Cache-Control"] = "private, no-store"

    return response
