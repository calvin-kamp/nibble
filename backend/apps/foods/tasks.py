from celery import shared_task
from django.core.management import call_command


@shared_task
def import_off_products():
    """Weekly job: refreshes the products from the Open Food Facts dump."""
    call_command("import_off_products")
