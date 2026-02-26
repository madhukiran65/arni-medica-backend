from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import BatchDeviation, BatchStep


@receiver(post_save, sender=BatchDeviation)
def update_batch_on_deviation_change(sender, instance, created, **kwargs):
    """Update batch deviation flag when a deviation is saved."""
    if instance.batch:
        instance.batch.update_deviation_flag()


@receiver(post_delete, sender=BatchDeviation)
def update_batch_on_deviation_delete(sender, instance, **kwargs):
    """Update batch deviation flag when a deviation is deleted."""
    if instance.batch:
        instance.batch.update_deviation_flag()
