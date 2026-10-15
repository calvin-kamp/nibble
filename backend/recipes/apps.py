from django.apps import AppConfig


class RecipesConfig(AppConfig):
    name = 'recipes'

    def ready(self):
        from . import signals  # noqa: F401
