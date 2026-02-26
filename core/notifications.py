"""
Email notification service for Arni eQMS
Handles email notifications for approvals, CAPAs, deviations, and reminders
"""
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending professional email notifications with Arni eQMS branding."""

    FRONTEND_BASE_URL = settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else 'http://localhost:3000'

    @staticmethod
    def _send_email(subject, recipient_email, context, template_name):
        """
        Generic method to send emails with HTML templates.

        Args:
            subject: Email subject line
            recipient_email: Email address to send to
            context: Dictionary of template variables
            template_name: Name of the template file to render

        Returns:
            True if successful, False if failed
        """
        try:
            # Render HTML template
            html_message = render_to_string(
                f'core/emails/{template_name}.html',
                context
            )
            plain_message = strip_tags(html_message)

            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                html_message=html_message,
                fail_silently=False,
            )
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
            return False

    @classmethod
    def send_approval_request(cls, document, approvers, requester):
        """
        Send approval request email to approvers.

        Args:
            document: Document object with id, title, status
            approvers: List of User objects to notify
            requester: User who requested approval
        """
        subject = f"Document Approval Required: {document.title}"

        for approver in approvers:
            context = {
                'approver_name': approver.get_full_name() or approver.username,
                'requester_name': requester.get_full_name() or requester.username,
                'document_title': document.title,
                'document_type': document.__class__.__name__,
                'approval_url': f"{cls.FRONTEND_BASE_URL}/documents/{document.id}/approve",
                'frontend_url': cls.FRONTEND_BASE_URL,
            }

            cls._send_email(
                subject=subject,
                recipient_email=approver.email,
                context=context,
                template_name='approval_request'
            )

    @classmethod
    def send_approval_complete(cls, document, approver, decision):
        """
        Send notification about approval decision to document owner.

        Args:
            document: Document object
            approver: User who made the decision
            decision: 'approved' or 'rejected'
        """
        status_text = "Approved" if decision == 'approved' else "Rejected"
        subject = f"Document {status_text}: {document.title}"

        context = {
            'owner_name': document.created_by.get_full_name() or document.created_by.username,
            'approver_name': approver.get_full_name() or approver.username,
            'document_title': document.title,
            'decision': status_text.lower(),
            'document_url': f"{cls.FRONTEND_BASE_URL}/documents/{document.id}",
            'frontend_url': cls.FRONTEND_BASE_URL,
        }

        cls._send_email(
            subject=subject,
            recipient_email=document.created_by.email,
            context=context,
            template_name='approval_complete'
        )

    @classmethod
    def send_capa_assignment(cls, capa, assignee):
        """
        Send notification when CAPA is assigned to a user.

        Args:
            capa: CAPA object with id, title
            assignee: User assigned to the CAPA
        """
        subject = f"CAPA Assigned: {capa.title}"

        context = {
            'assignee_name': assignee.get_full_name() or assignee.username,
            'capa_id': capa.id,
            'capa_title': capa.title,
            'capa_url': f"{cls.FRONTEND_BASE_URL}/capa/{capa.id}",
            'due_date': capa.due_date if hasattr(capa, 'due_date') else None,
            'frontend_url': cls.FRONTEND_BASE_URL,
        }

        cls._send_email(
            subject=subject,
            recipient_email=assignee.email,
            context=context,
            template_name='capa_assignment'
        )

    @classmethod
    def send_deviation_alert(cls, deviation, recipients):
        """
        Send critical deviation alert email.

        Args:
            deviation: Deviation object
            recipients: List of User objects to notify
        """
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

            cls._send_email(
                subject=subject,
                recipient_email=recipient.email,
                context=context,
                template_name='deviation_alert'
            )

    @classmethod
    def send_overdue_reminder(cls, record_type, record, assignee):
        """
        Send reminder for overdue items (CAPA, Training, etc).

        Args:
            record_type: Type of record ('CAPA', 'Training', 'Audit', etc)
            record: The record object
            assignee: User assigned to the record
        """
        subject = f"Reminder: Overdue {record_type} - {record.title}"

        # Determine URL based on record type
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

        cls._send_email(
            subject=subject,
            recipient_email=assignee.email,
            context=context,
            template_name='overdue_reminder'
        )

    @classmethod
    def send_training_reminder(cls, assignment, trainee):
        """
        Send training due reminder.

        Args:
            assignment: Training assignment object
            trainee: User who needs to complete training
        """
        subject = f"Training Due: {assignment.training.title}"

        context = {
            'trainee_name': trainee.get_full_name() or trainee.username,
            'training_title': assignment.training.title if hasattr(assignment, 'training') else assignment.title,
            'training_id': assignment.id,
            'due_date': assignment.due_date if hasattr(assignment, 'due_date') else None,
            'training_url': f"{cls.FRONTEND_BASE_URL}/training/{assignment.id}",
            'frontend_url': cls.FRONTEND_BASE_URL,
        }

        cls._send_email(
            subject=subject,
            recipient_email=trainee.email,
            context=context,
            template_name='training_reminder'
        )
