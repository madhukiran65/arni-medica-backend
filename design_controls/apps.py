from django.apps import AppConfig


class DesignControlsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'design_controls'
    verbose_name = 'Design Controls'

    def ready(self):
        import design_controls.signals  # noqa
