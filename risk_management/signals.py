from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import RiskMonitoringAlert


@receiver(post_save, sender=RiskMonitoringAlert)
def acknowledge_alert(sender, instance, created, **kwargs):
    """Automatically record acknowledgement timestamp when is_acknowledged is set"""
    if instance.is_acknowledged and not instance.acknowledged_at:
        instance.acknowledged_at = timezone.now()
        instance.save(update_fields=['acknowledged_at'])
