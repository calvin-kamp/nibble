import hashlib
import re

from rest_framework.throttling import SimpleRateThrottle

DURATIONS = {"s": 1, "m": 60, "h": 60 * 60, "d": 24 * 60 * 60}
PERIOD_PATTERN = re.compile(r"(?P<count>\d*)(?P<unit>[smhd])")


class RateThrottle(SimpleRateThrottle):
    """Also accepts periods with a multiplier, e.g. "5/15min" for five per 15 minutes."""

    def parse_rate(self, rate):
        if rate is None:
            return None, None

        num, period = rate.split("/")
        match = PERIOD_PATTERN.match(period)

        return int(num), int(match["count"] or 1) * DURATIONS[match["unit"]]


class IPThrottle(RateThrottle):
    """Counts requests per client IP, logged in or not."""

    def get_cache_key(self, request, view):
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }


class UserThrottle(RateThrottle):
    """Counts requests per logged-in user; anonymous requests pass."""

    scope = "user"

    def get_cache_key(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return None

        return self.cache_format % {"scope": self.scope, "ident": request.user.pk}


class AnonThrottle(IPThrottle):
    """Default limit for requests without login."""

    scope = "anon"

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            return None

        return super().get_cache_key(request, view)


class EmailThrottle(RateThrottle):
    """Counts requests per e-mail address in the body, stored only as hash."""

    def get_cache_key(self, request, view):
        email = str(request.data.get("email", "")).strip().lower()

        if not email:
            return None

        return self.cache_format % {
            "scope": self.scope,
            "ident": hashlib.sha256(email.encode()).hexdigest(),
        }
