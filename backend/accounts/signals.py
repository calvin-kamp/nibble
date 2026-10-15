from django.dispatch import Signal

# Sent with the user (sender=Profile, user=…) when the consent to store health
# data is withdrawn. Apps that keep health data delete it in a receiver, inside
# the same transaction as the profile update.
health_data_consent_revoked = Signal()

# Sent with the user (sender=Profile, user=…) to describe the health data that a
# revocation would delete. Each receiver returns a dict of counts, e.g.
# {"diary_entries": 142}; the consent view merges them for the dialog.
health_data_summary = Signal()

# Sent with the user (sender=Profile, user=…) for the data download. Each
# receiver returns a dict of top-level sections, e.g. {"diary": [...]}.
personal_data_export = Signal()
