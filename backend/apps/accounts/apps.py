from django.apps import AppConfig
from django.db.models.signals import post_delete


def log_deletion(sender, instance, **kwargs):
    """Every deleted account goes into the deletion log, also one deleted in the admin."""
    from .deletion_log import Event, record

    record(instance, Event.DELETED)


class AccountsConfig(AppConfig):
    name = "apps.accounts"

    def ready(self):
        post_delete.connect(
            log_deletion, sender=self.get_model("User"), dispatch_uid="log_deletion"
        )
