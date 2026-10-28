from accounts.models import User
from config.emails import send_email
from recipes.models import Recipe, RecipeSubmission


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
