from django.core.cache import cache
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.stats.services import CACHE_KEY, CACHE_SECONDS, collect_stats


class PublicStatsView(APIView):
    """Totals for the landing page. Public, so no cookie can turn it into a 401."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(cache.get_or_set(CACHE_KEY, collect_stats, CACHE_SECONDS))
