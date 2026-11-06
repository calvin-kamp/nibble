from rest_framework import status

from config.exceptions import ApiError, Conflict


class ProductExists(Conflict):
    default_code = "product_exists"
    default_detail = "Zu diesem Barcode gibt es schon ein Lebensmittel."


class OffUnavailable(ApiError):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_code = "off_unavailable"
    default_detail = (
        "Open Food Facts hat das Lebensmittel nicht angenommen. Es wurde nichts gespeichert, "
        "versuch es gleich noch einmal."
    )
