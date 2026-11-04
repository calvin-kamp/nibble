from django.contrib import admin

from .models import ConsentRecord, DeletionLog, Profile, User


class ConsentRecordInline(admin.TabularInline):
    """Read-only: the history is only ever added to through the API."""

    model = ConsentRecord
    fields = ("decided_at", "accepted", "policy_version")
    readonly_fields = fields
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    readonly_fields = ("created_at",)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "email_verified", "is_staff", "date_joined")
    list_filter = ("is_staff", "email_verified")
    search_fields = ("email", "profile__username")
    readonly_fields = ("password", "last_login", "date_joined")
    exclude = ("groups", "user_permissions")
    inlines = (ProfileInline,)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("__str__", "user", "consent_accepted", "onboarding_completed")
    readonly_fields = ("user", "created_at")
    inlines = (ConsentRecordInline,)


@admin.register(DeletionLog)
class DeletionLogAdmin(admin.ModelAdmin):
    """Read-only: entries come from the deletion flow and are needed after a restore."""

    list_display = ("occurred_at", "event", "user_id", "scheduled_for", "reported_at")
    list_filter = ("event",)
    search_fields = ("user_id",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
