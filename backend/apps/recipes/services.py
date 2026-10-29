import json
from decimal import Decimal
from pathlib import Path

from django.db import transaction
from django.utils import timezone
from rest_framework.utils.encoders import JSONEncoder

from apps.accounts.models import User
from apps.recipes.catalog.serializers import RecipeInputSerializer
from apps.recipes.exceptions import SubmissionNotPending
from apps.recipes.models import Recipe, RecipeIngredient, RecipeStep, RecipeSubmission
from config.emails import send_email


def notify_staff(submission):
    recipients = list(
        User.objects.filter(is_staff=True, is_active=True).values_list(
            "email", flat=True
        )
    )
    kind = (
        "Neues Rezept"
        if submission.kind == RecipeSubmission.Kind.NEW
        else "Änderungsvorschlag"
    )

    send_email(
        recipients,
        f"{kind}: {submission.content['name']}",
        f"Es gibt eine neue Einreichung zur Moderation ({kind}, "
        f"Einreichung {submission.pk}): {submission.content['name']}",
    )


def notify_author(submission):
    """Approval or rejection; notification only, so verified accounts only."""
    author = submission.recipe.author

    if author is None or not author.user.email_verified:
        return

    name = submission.content["name"]
    kind = (
        "Dein Rezept"
        if submission.kind == RecipeSubmission.Kind.NEW
        else "Deine Änderung am Rezept"
    )

    if submission.status == Recipe.Status.APPROVED:
        send_email(
            author.user.email,
            "Dein Rezept wurde freigegeben",
            f"{kind} „{name}“ wurde freigegeben und ist jetzt für alle sichtbar.",
        )
        return

    send_email(
        author.user.email,
        "Dein Rezept wurde abgelehnt",
        f"{kind} „{name}“ wurde leider abgelehnt.\n\n"
        f"Begründung:\n{submission.rejection_reason}",
    )


# Moderation workflow of recipes.
#
# A recipe that was never approved is edited in place and goes back to
# moderation. Once approved, the live version stays untouched: every change is
# collected in one open revision (content and/or image) until a moderator
# approves or rejects it.

Status = Recipe.Status
Kind = RecipeSubmission.Kind
ImageAction = RecipeSubmission.ImageAction

CONTENT_FIELDS = (
    "name",
    "description",
    "prep_time_minutes",
    "diet",
    "intolerances",
    "equipment",
    "meal_types",
    "servings",
    "kcal",
    "protein",
    "carbs",
    "fat",
)


def compute_properties(content):
    """See RecipeProperty in the API spec."""
    properties = []

    if content["protein"] > 0 and content["protein"] >= content["kcal"] * Decimal("0.1"):
        properties.append(Recipe.Property.PROTEIN_RICH)

    if content["kcal"] <= 450:
        properties.append(Recipe.Property.LOW_CALORIE)

    if len(content["ingredients"]) <= 5:
        properties.append(Recipe.Property.FEW_INGREDIENTS)

    if content["prep_time_minutes"] < 30:
        properties.append(Recipe.Property.UNDER_30_MIN)

    return properties


def content_json(content):
    """RecipeInput JSON of a Recipe or of validated data, as stored in submissions."""
    return json.loads(
        json.dumps(RecipeInputSerializer(content).data, cls=JSONEncoder)
    )


def apply_content(recipe, content):
    """Writes validated RecipeInput data into the recipe, its ingredients and steps."""
    for field in CONTENT_FIELDS:
        setattr(recipe, field, content[field])

    recipe.properties = compute_properties(content)
    recipe.save()

    recipe.ingredients.all().delete()
    RecipeIngredient.objects.bulk_create(
        RecipeIngredient(recipe=recipe, position=position, **ingredient)
        for position, ingredient in enumerate(content["ingredients"])
    )

    recipe.steps.all().delete()
    RecipeStep.objects.bulk_create(
        RecipeStep(recipe=recipe, **step) for step in content["steps"]
    )


def delete_file_on_commit(file):
    """Files can't be rolled back, so they go only once the data is gone for sure."""
    if not file:
        return

    storage, name = file.storage, file.name
    transaction.on_commit(lambda: storage.delete(name))


def open_submission(recipe, kind):
    return (
        recipe.submissions.select_for_update()
        .filter(kind=kind, status=Status.PENDING)
        .first()
    )


# ------------------------------------------------------------------------------
# Author actions
# ------------------------------------------------------------------------------


@transaction.atomic
def create_recipe(author, content):
    recipe = Recipe(author=author, status=Status.PENDING)
    apply_content(recipe, content)
    submit_new(recipe)

    return recipe


@transaction.atomic
def update_recipe(recipe, content):
    if recipe.status == Status.APPROVED:
        submit_revision(recipe, content=content)
        return

    recipe.status = Status.PENDING
    recipe.rejection_reason = None
    apply_content(recipe, content)
    submit_new(recipe)


@transaction.atomic
def replace_image(recipe, image):
    if recipe.status == Status.APPROVED:
        submit_revision(recipe, image=image)
        return

    delete_file_on_commit(recipe.image)
    recipe.image.save(image.name, image)


@transaction.atomic
def remove_image(recipe):
    if recipe.status == Status.APPROVED:
        submit_revision(recipe, remove_image=True)
        return

    delete_file_on_commit(recipe.image)
    recipe.image = ""
    recipe.save(update_fields=["image", "updated_at"])


@transaction.atomic
def delete_recipe(recipe):
    """Saved entries and submissions go with it via CASCADE, files on commit."""
    delete_file_on_commit(recipe.image)

    for submission in recipe.submissions.all():
        delete_file_on_commit(submission.image)

    recipe.delete()


def delete_submission(submission):
    delete_file_on_commit(submission.image)
    submission.delete()


def submit_new(recipe):
    """Keeps the open submission of a never approved recipe in sync with it."""
    submission = open_submission(recipe, Kind.NEW)

    if submission is not None:
        submission.content = content_json(recipe)
        submission.save(update_fields=["content"])
        return submission

    submission = RecipeSubmission.objects.create(
        recipe=recipe,
        kind=Kind.NEW,
        content=content_json(recipe),
    )
    notify_staff(submission)

    return submission


def submit_revision(recipe, content=None, image=None, remove_image=False):
    """Adds the change to the open revision, or starts one from the live version.

    Only a new revision notifies the staff, replacing an open one doesn't.
    """
    submission = open_submission(recipe, Kind.REVISION)
    is_new = submission is None

    if is_new:
        submission = RecipeSubmission(
            recipe=recipe,
            kind=Kind.REVISION,
            content=content_json(recipe),
        )

    if content is not None:
        submission.content = content_json(content)

    if image is not None or remove_image:
        delete_file_on_commit(submission.image)
        submission.image = ""
        submission.image_action = ImageAction.REMOVE

    if image is not None:
        submission.image.save(image.name, image, save=False)
        submission.image_action = ImageAction.REPLACE

    submission.save()

    if is_new:
        notify_staff(submission)

    return submission


# ------------------------------------------------------------------------------
# Moderator actions
# ------------------------------------------------------------------------------


def locked_pending(submission):
    submission = RecipeSubmission.objects.select_for_update().get(pk=submission.pk)

    if submission.status != Status.PENDING:
        raise SubmissionNotPending()

    return submission


@transaction.atomic
def approve(submission, moderator):
    submission = locked_pending(submission)
    recipe = submission.recipe

    if submission.kind == Kind.REVISION:
        serializer = RecipeInputSerializer(data=submission.content)
        serializer.is_valid(raise_exception=True)
        apply_content(recipe, serializer.validated_data)
        apply_revision_image(recipe, submission)

    recipe.status = Status.APPROVED
    recipe.rejection_reason = None
    recipe.save()

    submission.status = Status.APPROVED
    submission.reviewed_by = moderator
    submission.reviewed_at = timezone.now()
    submission.save()

    notify_author(submission)

    return submission


def apply_revision_image(recipe, submission):
    if submission.image_action == ImageAction.KEEP:
        return

    delete_file_on_commit(recipe.image)
    recipe.image = ""

    if submission.image_action == ImageAction.REPLACE:
        with submission.image.open("rb") as image:
            recipe.image.save(Path(submission.image.name).name, image, save=False)

        delete_file_on_commit(submission.image)
        submission.image = ""


@transaction.atomic
def reject(submission, moderator, reason):
    """The live version of an approved recipe stays as it is."""
    submission = locked_pending(submission)
    recipe = submission.recipe

    if submission.kind == Kind.NEW:
        recipe.status = Status.REJECTED
        recipe.rejection_reason = reason
        recipe.save(update_fields=["status", "rejection_reason", "updated_at"])

    submission.status = Status.REJECTED
    submission.rejection_reason = reason
    submission.reviewed_by = moderator
    submission.reviewed_at = timezone.now()
    submission.save()

    notify_author(submission)

    return submission
