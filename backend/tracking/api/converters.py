from datetime import date


class IsoDateConverter:
    """Matches "2026-10-14"; impossible dates like "2026-02-30" end in a 404."""

    regex = r"\d{4}-\d{2}-\d{2}"

    def to_python(self, value):
        # A ValueError makes Django treat the URL as not matching.
        return date.fromisoformat(value)

    def to_url(self, value):
        return value.isoformat()
