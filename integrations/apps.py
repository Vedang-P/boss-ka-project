from django.apps import AppConfig


class IntegrationsConfig(AppConfig):
    name = "integrations"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import integrations.services  # noqa: F401
