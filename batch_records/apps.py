from django.apps import AppConfig


class BatchRecordsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'batch_records'
    verbose_name = 'Batch Records'

    def ready(self):
        import batch_records.signals  # noqa
