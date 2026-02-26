"""
Email notification service for Arni eQMS
Handles email notifications for approvals, CAPAs, deviations, and reminders.
Also creates in-app Notification records for the notification center.
"""
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending professional email notifications with Arni eQMS branding."""

    FRONTEND_BASE_URL = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')

    @staticmethod
    def _create_in_app_notification(recipient, notification_type, subject, message,
                                     related_object_type='', related_object_id=''):
        """
        Create an in-app Notification record so users see it in the notification center.
        """
        try:
            from core.models import Notification
            Notification.objects.create(
                recipient=recipient,
                notification_type=notification_type,
                subject=subject,
                message=message,
                related_object_type=related_object_type,
                related_object_id=str(related_object_id) if related_object_id else '',
            )
        except Exception as e:
            logger.error(f"Failed to create in-app notification for {recipient}: {e}")

    @staticmethod
    def _send_email(subject, recipient_email, context, template_name):
        """
        Send email with HTML template. Returns True on success, False on failure.
        Falls back silently if email backend is console (dev mode).
        """
        try:
            html_message = render_to_string(
                f'core/emails/{template_name}.html',
                context
            )
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"Email sent to {recipient_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
            return False

    @classmethod
    def send_approval_request(cls, document, approvers, requester):
        """Send approval request email to approvers and create in-app notifications."""
        subject = f"Approval Required: {document.title}"

        for approver in approvers:
            context = {
                'approver_name': approver.get_full_name() or approver.username,
                'requester_name': requester.get_full_name() or requester.username,
                'document_title': document.title,
                'document_type': getattr(document, 'infocard_type', document.__class__.__name__),
                'approval_url': f"{cls.FRONTEND_BASE_URL}/documents/{document.id}/approve",
                'frontend_url': cls.FRONTEND_BASE_URL,
            }

            # Send email
            if approver.email:
                cls._send_email(
                    subject=subject,
                    recipient_email=approver.email,
                    context=context,
                    template_name='approval_request'
                )

            # Create in-app notification
            cls._create_in_app_notification(
                recipient=approver,
                notification_type='approval_request',
                subject=subject,
                message=f"{requester.get_full_name() or requester.username} has requested your approval for \"{document.title}\".",
                related_object_type='document',
                related_object_id=document.id,
            )

    @classmethod
    def send_approval_complete(cls, document, approver, decision):
        """Send notification about approval decision to document owner."""
        status_text = "Approved" if decision == 'approved' else "Rejected"
        subject = f"Document {status_text}: {document.title}"

        owner = getattr(document, 'created_by', None) or getattr(document, 'owner', None)
        if not owner:
            logger.warning(f"No owner found for document {document.id}, skipping notification")
            return

        context = {
            'owner_name': owner.get_full_name() or owner.username,
            'approver_name': approver.get_full_name() or approver.username,
            'document_title': document.title,
            'decision': status_text.lower(),
            'document_url': f"{cls.FRONTEND_BASE_URL}/documents/{document.id}",
            'frontend_url': cls.FRONTEND_BASE_URL,
        }

        if owner.email:
            cls._send_email(
                subject=subject,
                recipient_email=owner.email,
                context=context,
                template_name='approval_complete'
            )

        cls._create_in_app_notification(
            recipient=owner,
            notification_type='approval_complete',
            subject=subject,
            message=f"{approver.get_full_name() or approver.username} has {status_text.lower()} your document \"{document.title}\".",
            related_object_type='document',
            related_object_id=document.id,
        )

    @classmethod
    def send_workflow_transition(cls, record, from_stage, to_stage, transitioned_by, record_type='document'):
        """
        Send notification when a record transitions between workflow stages.
        Notifies the record owner and any relevant stakeholders.
        """
        record_title = getattr(record, 'title', str(record))
        subject = f"{record_type.title()} Stage Changed: {record_title} → {to_stage}"

        # Notify owner
        owner = (getattr(record, 'owner', None) or
                 getattr(record, 'created_by', None) or
                 getattr(record, 'initiator', None))

        if owner and owner != transitioned_by:
            message = (
                f"\"{record_title}\" has been moved from {from_stage} to {to_stage} "
                f"by {transitioned_by.get_full_name() or transitioned_by.username}."
            )

            # Determine URL based on record type
            url_map = {
                'document': f"{cls.FRONTEND_BASE_URL}/documents/{record.id}",
                'capa': f"{cls.FRONTEND_BASE_URL}/capa/{record.id}",
                'deviation': f"{cls.FRONTEND_BASE_URL}/deviations/{record.id}",
                'complaint': f"{cls.FRONTEND_BASE_URL}/complaints/{record.id}",
                'change_control': f"{cls.FRONTEND_BASE_URL}/change-controls/{record.id}",
            }

            context = {
                'recipient_name': owner.get_full_name() or owner.username,
                'record_title': record_title,
                'record_type': record_type.title(),
                'from_stage': from_stage,
                'to_stage': to_stage,
                'transitioned_by': transitioned_by.get_full_name() or transitioned_by.username,
                'record_url': url_map.get(record_type, f"{cls.FRONTEND_BASE_URL}/records/{record.id}"),
                'frontend_url': cls.FRONTEND_BASE_URL,
            }

            if owner.email:
                cls._send_email(
                    subject=subject,
                    recipient_email=owner.email,
                    context=context,
                    template_name='workflow_transition'
                )

            cls._create_in_app_notification(
                recipient=owner,
                notification_type='approval_request',
                subject=subject,
                message=message,
                related_object_type=record_type,
                related_object_id=record.id,
            )

    @classmethod
    def send_capa_assignment(cls, capa, assignee):
        """Send notification when CAPA is assigned to a user."""
        subject = f"CAPA Assigned: {capa.title}"

        context = {
            'assignee_name': assignee.get_full_name() or assignee.username,
            'capa_id': capa.id,
            'capa_title': capa.title,
            'capa_url': f"{cls.FRONTEND_BASE_URL}/capa/{capa.id}",
            'due_date': capa.due_date if hasattr(capa, 'due_date') else None,
            'frontend_url': cls.FRONTEND_BASE_URL,
        }

        if assignee.email:
            cls._send_email(
                subject=subject,
                recipient_email=assignee.email,
                context=context,
                template_name='capa_assignment'
            )

        cls._create_in_app_notification(
            recipient=assignee,
            notification_type='capa_assignment',
            subject=subject,
            message=f"You have been assigned CAPA \"{capa.title}\".",
            related_object_type='capa',
            related_object_id=capa.id,
        )

    @classmethod
    def send_deviation_alert(cls, deviation, recipients):
        """Send critical deviation alert email."""
        severity = getattr(deviation, 'severity', 'High')
        subject = f"CRITICAL: Deviation Alert - {deviation.title} ({severity})"

        for recipient in recipients:
            context = {
                'recipient_name': recipient.get_full_name() or recipient.username,
                'deviation_id': deviation.id,
                'deviation_title': deviation.title,
                'severity': severity,
                'description': getattr(deviation, 'description', ''),
                'deviation_url': f"{cls.FRONTEND_BASE_URL}/deviations/{deviation.id}",
                'frontend_url': cls.FRONTEND_BASE_URL,
            }

            if recipient.email:
                cls._send_email(
                    subject=subject,
                    recipient_email=recipient.email,
                    context=context,
                    template_name='deviation_alert'
                )

            cls._create_in_app_notification(
                recipient=recipient,
                notification_type='deviation_alert',
                subject=subject,
                message=f"Deviation \"{deviation.title}\" ({severity}) requires immediate attention.",
                related_object_type='deviation',
                related_object_id=deviation.id,
            )

    @classmethod
    def send_overdue_reminder(cls, record_type, record, assignee):
        """Send reminder for overdue items (CAPA, Training, etc)."""
        subject = f"Reminder: Overdue {record_type} - {record.title}"

        url_map = {
            'CAPA': f"{cls.FRONTEND_BASE_URL}/capa/{record.id}",
            'Training': f"{cls.FRONTEND_BASE_URL}/training/{record.id}",
            'Deviation': f"{cls.FRONTEND_BASE_URL}/deviations/{record.id}",
            'Audit': f"{cls.FRONTEND_BASE_URL}/audits/{record.id}",
        }
        record_url = url_map.get(record_type, f"{cls.FRONTEND_BASE_URL}/records/{record.id}")

        context = {
            'assignee_name': assignee.get_full_name() or assignee.username,
            'record_type': record_type,
            'record_title': record.title,
            'due_date': getattr(record, 'due_date', None),
            'record_url': record_url,
            'frontend_url': cls.FRONTEND_BASE_URL,
        }

        if assignee.email:
            cls._send_email(
                subject=subject,
                recipient_email=assignee.email,
                context=context,
                template_name='overdue_reminder'
            )

        cls._create_in_app_notification(
            recipient=assignee,
            notification_type='overdue_reminder',
            subject=subject,
            message=f"Your {record_type} \"{record.title}\" is overdue.",
            related_object_type=record_type.lower(),
            related_object_id=record.id,
        )

    @classmethod
    def send_training_reminder(cls, assignment, trainee):
        """Send training due reminder."""
        training_title = assignment.training.title if hasattr(assignment, 'training') else assignment.title
        subject = f"Training Due: {training_title}"

        context = {
            'trainee_name': trainee.get_full_name() or trainee.username,
            'training_title': training_title,
            'training_id': assignment.id,
            'due_date': assignment.due_date if hasattr(assignment, 'due_date') else None,
            'training_url': f"{cls.FRONTEND_BASE_URL}/training/{assignment.id}",
            'frontend_url': cls.FRONTEND_BASE_URL,
        }

        if trainee.email:
            cls._send_email(
                subject=subject,
                recipient_email=trainee.email,
                context=context,
                template_name='training_reminder'
            )

        cls._create_in_app_notification(
            recipient=trainee,
            notification_type='training_reminder',
            subject=subject,
            message=f"Your training \"{training_title}\" is due soon.",
            related_object_type='training',
            related_object_id=assignment.id,
        )

    @classmethod
    def send_test_email(cls, recipient_email, recipient_name='User'):
        """Send a test email to verify SMTP configuration."""
        subject = "Arni eQMS - Email Configuration Test"
        context = {
            'recipient_name': recipient_name,
            'frontend_url': cls.FRONTEND_BASE_URL,
        }
        return cls._send_email(
            subject=subject,
            recipient_email=recipient_email,
            context=context,
            template_name='test_email'
        )
