"""Onboarding rules: username -> consent -> goal -> targets -> summary.

Saving a step's data moves the user on by itself (see advance()). PATCH
/onboarding only covers jumps the backend can't see, e.g. "later" on the targets.
"""

from accounts.models import Profile

Step = Profile.OnboardingStep


def is_allowed(profile, step):
    if profile.onboarding_completed:
        return False

    if step == Step.USERNAME:
        return True

    if not profile.username:
        return False

    if step in (Step.GOAL, Step.TARGETS):
        return profile.consent_accepted is True

    if step == Step.SUMMARY:
        return profile.consent_accepted is not None

    return True


def go_to(profile, step):
    profile.onboarding_step = step
    profile.save(update_fields=["onboarding_step"])


def advance(profile, done_step, next_step):
    """Moves on after a step was saved, but only while the user is on that step."""
    if not profile.onboarding_completed and profile.onboarding_step == done_step:
        go_to(profile, next_step)


def after_consent_decision(profile):
    if profile.consent_accepted:
        advance(profile, Step.CONSENT, Step.GOAL)
        return

    # Declining skips goal and targets; revoking mid-way leaves them, too.
    if not profile.onboarding_completed and profile.onboarding_step in (
        Step.CONSENT,
        Step.GOAL,
        Step.TARGETS,
    ):
        go_to(profile, Step.SUMMARY)
