"""
Celery periodic tasks for document lifecycle management.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_overdue_reviews():
    """Check for documents past their review date and send notifications."""
    from documents.models import Document
    today = timezone.now().date()

    overdue_docs = Document.objects.filter(
        vault_state='effective',
        next_review_date__lt=today,
    ).select_related('owner')

    count = 0
    for doc in overdue_docs:
        try:
            from core.notifications import NotificationService
            NotificationService.send_notification(
                user=doc.owner,
                title=f'OVERDUE Review: {doc.document_id}',
                message=f'Document "{doc.title}" review was due on {doc.next_review_date}. Please initiate a review.',
                notification_type='review_overdue',
                related_object=doc,
            )
            count += 1
        except Exception as e:
            logger.warning(f"Failed to notify for {doc.document_id}: {e}")

    return f"Notified {count} overdue document reviews"


@shared_task
def check_training_completion():
    """Check if all training is complete for documents in training_period."""
    from documents.models import Document

    docs_in_training = Document.objects.filter(vault_state='training_period')

    transitioned = 0
    for doc in docs_in_training:
        try:
            from training.models import TrainingAssignment
            assignments = TrainingAssignment.objects.filter(triggering_document=doc)
            total = assignments.count()
            completed = assignments.filter(status='completed').count()

            if total > 0 and completed == total:
                doc.vault_state = 'effective'
                doc.lifecycle_stage = 'effective'
                doc.effective_date = timezone.now().date()
                doc.training_completed_date = timezone.now()

                if doc.review_period_months:
                    try:
                        from dateutil.relativedelta import relativedelta
                        doc.next_review_date = timezone.now().date() + relativedelta(months=doc.review_period_months)
                    except ImportError:
                        doc.next_review_date = timezone.now().date() + timedelta(days=doc.review_period_months * 30)

                doc.save()
                transitioned += 1
                logger.info(f"Document {doc.document_id} auto-transitioned to effective (training complete)")
        except Exception as e:
            logger.warning(f"Training check failed for {doc.document_id}: {e}")

    return f"Transitioned {transitioned} documents from training_period to effective"


@shared_task
def send_review_reminders():
    """Send reminders for documents approaching their review date (30 days before)."""
    from documents.models import Document
    today = timezone.now().date()
    reminder_date = today + timedelta(days=30)

    upcoming_reviews = Document.objects.filter(
        vault_state='effective',
        next_review_date__lte=reminder_date,
        next_review_date__gt=today,
    ).select_related('owner')

    count = 0
    for doc in upcoming_reviews:
        try:
            from core.notifications import NotificationService
            days_until = (doc.next_review_date - today).days
            NotificationService.send_notification(
                user=doc.owner,
                title=f'Review Reminder: {doc.document_id}',
                message=f'Document "{doc.title}" review is due in {days_until} days ({doc.next_review_date}).',
                notification_type='review_reminder',
                related_object=doc,
            )
            count += 1
        except Exception as e:
            logger.warning(f"Review reminder failed for {doc.document_id}: {e}")

    return f"Sent {count} review reminders"


@shared_task
def escalate_overdue_approvals():
    """Escalate approval requests that have been pending too long (>5 business days)."""
    from documents.models import Document, DocumentApprover

    cutoff = timezone.now() - timedelta(days=7)

    stale_approvals = DocumentApprover.objects.filter(
        approval_status='pending',
        document__vault_state='in_review',
        document__updated_at__lt=cutoff,
    ).select_related('document', 'approver')

    count = 0
    for approval in stale_approvals:
        try:
            from core.notifications import NotificationService
            NotificationService.send_notification(
                user=approval.approver,
                title=f'ESCALATION: Pending Approval for {approval.document.document_id}',
                message=f'Your approval for "{approval.document.title}" has been pending for over 7 days. Please review.',
                notification_type='approval_escalation',
                related_object=approval.document,
            )
            count += 1
        except Exception as e:
            logger.warning(f"Escalation failed for approval {approval.id}: {e}")

    return f"Escalated {count} overdue approvals"
