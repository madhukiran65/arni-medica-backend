from django.apps import AppConfig


class RiskManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'risk_management'
    verbose_name = 'Risk Management (ISO 14971)'

    def ready(self):
        import risk_management.signals  # noqa
