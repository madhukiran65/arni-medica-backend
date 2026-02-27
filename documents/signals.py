import hashlib
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from documents.models import Document, DocumentVersion


@receiver(pre_save, sender=Document)
def calculate_document_file_hash(sender, instance, **kwargs):
    """Calculate SHA-256 hash of the uploaded file."""
    if instance.file:
        if instance.file.size > 0:
            # Read file content and calculate hash
            instance.file.seek(0)
            file_hash = hashlib.sha256(instance.file.read()).hexdigest()
            instance.file_hash = file_hash
            instance.file.seek(0)


@receiver(post_save, sender=Document)
def create_initial_document_version(sender, instance, created, **kwargs):
    """Create initial document version when document is created."""
    if created:
        DocumentVersion.objects.create(
            document=instance,
            major_version=instance.major_version,
            minor_version=instance.minor_version,
            created_by=instance.owner or instance.created_by,
            updated_by=instance.owner or instance.created_by,
            change_summary='Initial version',
            snapshot_data={
                'title': instance.title,
                'vault_state': instance.vault_state,
                'created_at': str(instance.created_at) if instance.created_at else None,
            },
        )


@receiver(post_save, sender=Document)
def auto_assign_training_on_approval(sender, instance, **kwargs):
    """Auto-assign training when document enters training_period state."""
    if instance.vault_state == 'training_period' and instance.requires_training:
        try:
            from training.models import TrainingAssignment
            from django.contrib.auth.models import User

            # Get applicable roles
            applicable_roles = instance.training_applicable_roles or []

            if applicable_roles:
                # Find users with these roles
                users = User.objects.filter(
                    profile__roles__name__in=applicable_roles
                ).distinct()
            else:
                # If no roles specified, assign to department users
                if instance.department:
                    users = User.objects.filter(
                        profile__department=instance.department
                    ).distinct()
                else:
                    users = User.objects.none()

            for user in users:
                TrainingAssignment.objects.get_or_create(
                    triggering_document=instance,
                    trainee=user,
                    defaults={
                        'auto_triggered': True,
                        'status': 'assigned',
                        'created_by': instance.updated_by or instance.owner,
                        'updated_by': instance.updated_by or instance.owner,
                    }
                )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Auto-assign training failed: {e}")


@receiver(post_save, sender=Document)
def notify_periodic_review_due(sender, instance, **kwargs):
    """Send notification when document is approaching review date."""
    if instance.vault_state == 'effective' and instance.next_review_date:
        from django.utils import timezone
        from datetime import timedelta
        today = timezone.now().date()
        warning_date = instance.next_review_date - timedelta(days=30)

        if today >= warning_date and today < instance.next_review_date:
            try:
                from core.notifications import NotificationService
                NotificationService.send_notification(
                    user=instance.owner,
                    title=f'Periodic Review Due: {instance.document_id}',
                    message=f'Document "{instance.title}" is due for periodic review on {instance.next_review_date}.',
                    notification_type='review_reminder',
                    related_object=instance,
                )
            except Exception:
                pass
