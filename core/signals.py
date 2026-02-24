"""
Django signals for automatic audit logging.
Captures all create/update/delete on AuditedModel subclasses.
"""
import logging
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from core.models import AuditedModel, AuditLog

logger = logging.getLogger('core.audit')

# Thread-local storage for request context (set by middleware)
import threading
_thread_locals = threading.local()


def get_current_user():
    return getattr(_thread_locals, 'user', None)


def get_current_ip():
    return getattr(_thread_locals, 'ip_address', None)


def set_request_context(user, ip_address):
    _thread_locals.user = user
    _thread_locals.ip_address = ip_address


def clear_request_context():
    _thread_locals.user = None
    _thread_locals.ip_address = None


@receiver(pre_save)
def capture_old_values(sender, instance, **kwargs):
    """Capture old values before save for audit comparison."""
    if not issubclass(sender, AuditedModel):
        return
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_values = {
                f.name: str(getattr(old_instance, f.name))
                for f in sender._meta.fields
                if f.name not in ('updated_at',)
            }
        except sender.DoesNotExist:
            instance._old_values = {}
    else:
        instance._old_values = {}


@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    """Log create/update to audit trail."""
    if not issubclass(sender, AuditedModel):
        return
    if sender == AuditLog:
        return  # Don't log audit logs

    user = get_current_user()
    if not user or not user.is_authenticated:
        return

    ct = ContentType.objects.get_for_model(sender)
    action = 'create' if created else 'update'

    new_values = {
        f.name: str(getattr(instance, f.name))
        for f in sender._meta.fields
        if f.name not in ('updated_at',)
    }
    old_values = getattr(instance, '_old_values', {})

    # Only log if something actually changed
    if not created:
        changes = {k: v for k, v in new_values.items() if old_values.get(k) != v}
        if not changes:
            return
        change_summary = '; '.join(f"{k}: {old_values.get(k, '')} → {v}" for k, v in changes.items())
    else:
        change_summary = f"Created {sender.__name__}: {instance}"

    try:
        AuditLog.objects.create(
            content_type=ct,
            object_id=str(instance.pk),
            object_repr=str(instance)[:255],
            user=user,
            action=action,
            ip_address=get_current_ip(),
            old_values=old_values,
            new_values=new_values,
            change_summary=change_summary,
        )
        logger.info(f"Audit: {action} {sender.__name__} {instance.pk} by {user}")
    except Exception as e:
        logger.error(f"Audit log failed: {e}")


@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    """Log deletion to audit trail."""
    if not issubclass(sender, AuditedModel):
        return

    user = get_current_user()
    if not user or not user.is_authenticated:
        return

    ct = ContentType.objects.get_for_model(sender)
    old_values = {
        f.name: str(getattr(instance, f.name))
        for f in sender._meta.fields
    }

    try:
        AuditLog.objects.create(
            content_type=ct,
            object_id=str(instance.pk),
            object_repr=str(instance)[:255],
            user=user,
            action='delete',
            ip_address=get_current_ip(),
            old_values=old_values,
            new_values={},
            change_summary=f"Deleted {sender.__name__}: {instance}",
        )
    except Exception as e:
        logger.error(f"Audit log (delete) failed: {e}")
