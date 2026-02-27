"""
Celery configuration for Arni Medica eQMS.
ISO 13485 | FDA 21 CFR Part 11/820 | CDSCO MDR | EU IVDR Compliant
"""
import os
from celery import Celery

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('arni_eqms')

# Load configuration from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    'check-overdue-reviews-daily': {
        'task': 'documents.tasks.check_overdue_reviews',
        'schedule': 86400.0,  # Every 24 hours
    },
    'check-training-completion-hourly': {
        'task': 'documents.tasks.check_training_completion',
        'schedule': 3600.0,  # Every hour
    },
    'send-review-reminders-daily': {
        'task': 'documents.tasks.send_review_reminders',
        'schedule': 86400.0,  # Every 24 hours
    },
    'escalate-overdue-approvals-daily': {
        'task': 'documents.tasks.escalate_overdue_approvals',
        'schedule': 86400.0,  # Every 24 hours
    },
}

@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    print(f'Request: {self.request!r}')
