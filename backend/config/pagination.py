from rest_framework.pagination import PageNumberPagination


class PagePagination(PageNumberPagination):
    """Fixed pages of 12 for recipes, moderation and the food search."""

    page_size = 12
