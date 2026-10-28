from django.db import transaction

from recipes.models import Recipe, RecipeSubmission
from recipes.services.submissions import delete_recipe, delete_submission


@transaction.atomic
def delete_account(user):
    """Deletes the user and everything attached; approved recipes stay without author.

    Profile, consent, goals, tracking data, meals and saved recipes go with the
    profile via CASCADE. Recipes only get their author set to NULL, so the ones
    that were never approved and all unapproved revisions are removed here.
    """
    profile = user.profile

    for recipe in Recipe.objects.filter(author=profile).exclude(
        status=Recipe.Status.APPROVED
    ):
        delete_recipe(recipe)

    for submission in RecipeSubmission.objects.filter(
        recipe__author=profile,
        kind=RecipeSubmission.Kind.REVISION,
    ).exclude(status=Recipe.Status.APPROVED):
        delete_submission(submission)

    user.delete()
