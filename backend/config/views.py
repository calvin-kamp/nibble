from django.http import JsonResponse

from .exceptions import MESSAGES


def not_found(request, exception=None):
    """JSON instead of Django's HTML page for unknown URLs (DEBUG=False only)."""
    return JsonResponse(
        {"code": "not_found", "message": MESSAGES["not_found"]}, status=404
    )


def server_error(request):
    return JsonResponse(
        {
            "code": "server_error",
            "message": "Ein unerwarteter Fehler ist aufgetreten.",
        },
        status=500,
    )
