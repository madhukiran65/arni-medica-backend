"""
Workflow Engine Service Layer.
All workflow transitions go through here — never bypass this service.
Provides validation, audit logging, and electronic signature enforcement.
"""
import logging
from datetime import timedelta

from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from core.models import AuditLog, ElectronicSignature
from .models import (
    WorkflowDefinition, WorkflowStage, WorkflowTransition,
    WorkflowRecord, WorkflowHistory, WorkflowApprovalGate,
    WorkflowApprovalRequest, WorkflowDelegation,
)

logger = logging.getLogger('workflows.services')


class WorkflowError(Exception):
    """Base exception for workflow operations."""
    pass


class TransitionNotAllowed(WorkflowError):
    """Raised when a transition is not permitted."""
    pass


class ApprovalRequired(WorkflowError):
    """Raised when approvals are needed before transition."""
    pass


class FieldValidationError(WorkflowError):
    """Raised when required fields are missing."""
    pass


class SignatureRequired(WorkflowError):
    """Raised when an electronic signature is required."""
    pass


class WorkflowService:
    """
    Core workflow orchestration. Every state transition goes through here.
    Enforces: legal transitions, permissions, field validation, approval gates,
    electronic signatures, and audit logging.
    """

    @staticmethod
    @transaction.atomic
    def initialize_workflow(record, workflow_name, model_type, user, ip_address=None):
        """
        Attach a workflow to a new EQMS record.
        Sets the record to the initial stage.

        Args:
            record: The EQMS model instance (Document, CAPA, etc.)
            workflow_name: Name of the WorkflowDefinition
            model_type: Module type string (e.g., 'document', 'capa')
            user: The user creating the record
            ip_address: Optional client IP

        Returns:
            WorkflowRecord instance
        """
        try:
            workflow = WorkflowDefinition.objects.get(
                name=workflow_name, model_type=model_type, is_active=True
            )
        except WorkflowDefinition.DoesNotExist:
            raise WorkflowError(
                f"No active workflow '{workflow_name}' found for '{model_type}'"
            )

        initial_stage = workflow.stages.filter(is_initial=True).first()
        if not initial_stage:
            raise WorkflowError(
                f"Workflow '{workflow_name}' has no initial stage defined"
            )

        content_type = ContentType.objects.get_for_model(record)

        # Calculate SLA deadline
        estimated_exit = None
        if initial_stage.sla_days:
            estimated_exit = timezone.now() + timedelta(days=initial_stage.sla_days)

        workflow_record = WorkflowRecord.objects.create(
            workflow=workflow,
            current_stage=initial_stage,
            content_type=content_type,
            object_id=str(record.pk),
            estimated_exit_date=estimated_exit,
        )

        # Create audit log
        AuditLog.objects.create(
            content_type=content_type,
            object_id=str(record.pk),
            object_repr=str(record),
            user=user,
            action='transition',
            ip_address=ip_address,
            new_values={
                'workflow': workflow.name,
                'stage': initial_stage.name,
                'action': 'workflow_initialized',
            },
            change_summary=f"Workflow '{workflow.name}' initialized at stage '{initial_stage.name}'"
        )

        # Create approval requests if initial stage requires them
        if initial_stage.requires_approval:
            WorkflowService._create_approval_requests(workflow_record, initial_stage)

        logger.info(
            f"Workflow initialized: {record} → {initial_stage.name} by {user}"
        )
        return workflow_record

    @staticmethod
    @transaction.atomic
    def transition(workflow_record, to_stage_slug, user, comments='',
                   signature_password=None, ip_address=None):
        """
        Transition a record to a new stage.

        Validation chain:
        1. Check transition is legal (exists in WorkflowTransition)
        2. Check user has permission
        3. Validate required fields on target stage
        4. Check approval gates are satisfied
        5. Create electronic signature (if required)
        6. Create WorkflowHistory record
        7. Update WorkflowRecord.current_stage
        8. Create AuditLog entry

        Args:
            workflow_record: The WorkflowRecord to transition
            to_stage_slug: Slug of the target stage
            user: User performing the transition
            comments: Optional transition comment
            signature_password: Password for e-signature (if required)
            ip_address: Client IP address

        Returns:
            Updated WorkflowRecord

        Raises:
            TransitionNotAllowed, ApprovalRequired, FieldValidationError, SignatureRequired
        """
        from_stage = workflow_record.current_stage
        workflow = workflow_record.workflow

        # 1. Find target stage
        try:
            to_stage = workflow.stages.get(slug=to_stage_slug)
        except WorkflowStage.DoesNotExist:
            raise TransitionNotAllowed(
                f"Stage '{to_stage_slug}' does not exist in workflow '{workflow.name}'"
            )

        # 2. Check transition is legal
        try:
            transition_def = WorkflowTransition.objects.get(
                workflow=workflow, from_stage=from_stage, to_stage=to_stage
            )
        except WorkflowTransition.DoesNotExist:
            raise TransitionNotAllowed(
                f"Transition from '{from_stage.name}' to '{to_stage.name}' is not allowed"
            )

        # 3. Check permissions
        if transition_def.required_permission:
            if not user.has_perm(transition_def.required_permission):
                raise TransitionNotAllowed(
                    f"User lacks required permission: {transition_def.required_permission}"
                )

        if transition_def.required_roles:
            user_roles = set()
            if hasattr(user, 'profile') and hasattr(user.profile, 'roles'):
                user_roles = set(user.profile.roles.values_list('name', flat=True))
            required_roles = set(transition_def.required_roles)
            if not user_roles.intersection(required_roles):
                raise TransitionNotAllowed(
                    f"User does not have required role(s): {transition_def.required_roles}"
                )

        # 4. Validate required fields on the underlying record
        if to_stage.required_fields:
            record = workflow_record.content_object
            missing_fields = []
            for field_name in to_stage.required_fields:
                value = getattr(record, field_name, None)
                if value is None or value == '' or value == []:
                    missing_fields.append(field_name)
            if missing_fields:
                raise FieldValidationError(
                    f"Required fields missing for stage '{to_stage.name}': {missing_fields}"
                )

        # 5. Check approval gates are satisfied (for FROM stage)
        if from_stage.requires_approval:
            approval_status = WorkflowService.get_approval_status(workflow_record)
            if not approval_status['is_satisfied']:
                raise ApprovalRequired(
                    f"Approvals not complete for stage '{from_stage.name}': "
                    f"{approval_status['pending_count']} pending"
                )

        # 6. Handle electronic signature
        signature = None
        if from_stage.requires_signature or to_stage.requires_signature:
            if not signature_password:
                raise SignatureRequired(
                    f"Electronic signature required for transition to '{to_stage.name}'"
                )
            # Verify password
            if not user.check_password(signature_password):
                raise SignatureRequired("Invalid signature password")

            # Create electronic signature
            content_type = workflow_record.content_type
            record = workflow_record.content_object
            reason = from_stage.signature_reason or to_stage.signature_reason or 'approval'
            meaning = (
                f"Transitioning {record} from '{from_stage.name}' to '{to_stage.name}'. "
                f"Comments: {comments}"
            )
            signature = ElectronicSignature.create_signature(
                user=user,
                content_type=content_type,
                object_id=workflow_record.object_id,
                content_str=f"{workflow_record.pk}|{from_stage.pk}|{to_stage.pk}|{timezone.now().isoformat()}",
                reason=reason,
                meaning=meaning,
                ip_address=ip_address,
            )

        # 7. Calculate time in previous stage
        time_in_stage = None
        if workflow_record.entered_stage_at:
            delta = timezone.now() - workflow_record.entered_stage_at
            time_in_stage = int(delta.total_seconds())

        # 8. Create immutable history record
        WorkflowHistory.objects.create(
            workflow_record=workflow_record,
            from_stage=from_stage,
            to_stage=to_stage,
            transition=transition_def,
            transitioned_by=user,
            comments=comments,
            ip_address=ip_address,
            time_in_stage_seconds=time_in_stage,
            signature=signature,
        )

        # 9. Update workflow record
        estimated_exit = None
        if to_stage.sla_days:
            estimated_exit = timezone.now() + timedelta(days=to_stage.sla_days)

        workflow_record.current_stage = to_stage
        workflow_record.entered_stage_at = timezone.now()
        workflow_record.estimated_exit_date = estimated_exit
        workflow_record.is_overdue = False
        workflow_record.stage_entry_count = (
            WorkflowHistory.objects.filter(
                workflow_record=workflow_record, to_stage=to_stage
            ).count()
        )
        workflow_record.save()

        # 10. Create audit log
        content_type = workflow_record.content_type
        AuditLog.objects.create(
            content_type=content_type,
            object_id=workflow_record.object_id,
            object_repr=str(workflow_record.content_object),
            user=user,
            action='transition',
            ip_address=ip_address,
            old_values={'stage': from_stage.name},
            new_values={'stage': to_stage.name},
            change_summary=(
                f"Transitioned from '{from_stage.name}' to '{to_stage.name}'. "
                f"{comments}"
            ),
        )

        # 11. Create approval requests for new stage if needed
        if to_stage.requires_approval:
            WorkflowService._create_approval_requests(workflow_record, to_stage)

        logger.info(
            f"Transition: {workflow_record.content_object} "
            f"'{from_stage.name}' → '{to_stage.name}' by {user}"
        )
        return workflow_record

    @staticmethod
    def get_valid_transitions(workflow_record):
        """
        Return list of stages the record can transition to from current stage.

        Returns:
            List of dicts with transition details:
            [{'stage': WorkflowStage, 'transition': WorkflowTransition, 'label': str}, ...]
        """
        current_stage = workflow_record.current_stage
        transitions = WorkflowTransition.objects.filter(
            workflow=workflow_record.workflow,
            from_stage=current_stage,
        ).select_related('to_stage')

        results = []
        for t in transitions:
            results.append({
                'stage_id': t.to_stage.id,
                'stage_name': t.to_stage.name,
                'stage_slug': t.to_stage.slug,
                'label': t.label or f"Move to {t.to_stage.name}",
                'button_color': t.button_color,
                'requires_comment': t.requires_comment,
                'is_rejection': t.is_rejection,
                'requires_signature': t.to_stage.requires_signature or current_stage.requires_signature,
                'required_permission': t.required_permission,
                'required_roles': t.required_roles,
            })
        return results

    @staticmethod
    def get_approval_status(workflow_record):
        """
        Check approval status for current stage.

        Returns:
            dict with:
            - is_satisfied: bool (all gates met)
            - gates: list of gate statuses
            - pending_count: total pending approvals
            - approved_count: total approved
            - rejected_count: total rejected
        """
        current_stage = workflow_record.current_stage
        gates = WorkflowApprovalGate.objects.filter(
            stage=current_stage
        ).prefetch_related('requests')

        if not gates.exists():
            return {
                'is_satisfied': True,
                'gates': [],
                'pending_count': 0,
                'approved_count': 0,
                'rejected_count': 0,
            }

        gate_statuses = []
        total_pending = 0
        total_approved = 0
        total_rejected = 0
        all_satisfied = True

        for gate in gates:
            requests = gate.requests.filter(workflow_record=workflow_record)
            approved = requests.filter(status='approved').count()
            rejected = requests.filter(status='rejected').count()
            pending = requests.filter(status='pending').count()

            total_pending += pending
            total_approved += approved
            total_rejected += rejected

            # Check if this gate is satisfied
            if gate.approval_mode == 'all':
                gate_satisfied = (approved >= gate.required_count and pending == 0)
            elif gate.approval_mode == 'any':
                gate_satisfied = approved >= 1
            elif gate.approval_mode == 'majority':
                total = requests.count()
                gate_satisfied = approved > total / 2
            elif gate.approval_mode == 'count':
                gate_satisfied = approved >= gate.required_count
            else:
                gate_satisfied = approved >= gate.required_count

            if not gate_satisfied:
                all_satisfied = False

            gate_statuses.append({
                'gate_id': gate.id,
                'gate_name': gate.name,
                'required_role': gate.required_role,
                'required_count': gate.required_count,
                'approval_mode': gate.approval_mode,
                'approved_count': approved,
                'rejected_count': rejected,
                'pending_count': pending,
                'is_satisfied': gate_satisfied,
            })

        return {
            'is_satisfied': all_satisfied,
            'gates': gate_statuses,
            'pending_count': total_pending,
            'approved_count': total_approved,
            'rejected_count': total_rejected,
        }

    @staticmethod
    @transaction.atomic
    def respond_to_approval(approval_request, status, user, comments='',
                            signature_password=None, ip_address=None):
        """
        Respond to an approval request.

        Args:
            approval_request: WorkflowApprovalRequest instance
            status: 'approved' or 'rejected'
            user: User responding
            comments: Response comments
            signature_password: Password for e-signature
            ip_address: Client IP

        Returns:
            Updated WorkflowApprovalRequest
        """
        if status not in ('approved', 'rejected', 'deferred'):
            raise WorkflowError(f"Invalid approval status: {status}")

        if approval_request.approver != user:
            # Check delegation
            delegations = WorkflowDelegation.objects.filter(
                delegator=approval_request.approver,
                delegate=user,
                is_active=True,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now(),
            )
            if not delegations.exists():
                raise WorkflowError(
                    "You are not the assigned approver and have no active delegation"
                )

        # Handle signature if gate's stage requires it
        signature = None
        gate = approval_request.gate
        if gate.stage.requires_signature:
            if not signature_password:
                raise SignatureRequired("Electronic signature required for approval")
            if not user.check_password(signature_password):
                raise SignatureRequired("Invalid signature password")

            wr = approval_request.workflow_record
            signature = ElectronicSignature.create_signature(
                user=user,
                content_type=wr.content_type,
                object_id=wr.object_id,
                content_str=f"approval|{approval_request.pk}|{status}|{timezone.now().isoformat()}",
                reason='approval',
                meaning=f"Approval response: {status}. {comments}",
                ip_address=ip_address,
            )

        approval_request.respond(status=status, comments=comments, signature=signature)

        # Create audit log
        wr = approval_request.workflow_record
        AuditLog.objects.create(
            content_type=wr.content_type,
            object_id=wr.object_id,
            object_repr=str(wr.content_object),
            user=user,
            action='approve' if status == 'approved' else 'reject',
            ip_address=ip_address,
            new_values={
                'gate': gate.name,
                'status': status,
                'comments': comments,
            },
            change_summary=f"Approval '{gate.name}': {status}. {comments}",
        )

        # Check if auto-advance is enabled and all gates satisfied
        if gate.stage.auto_advance and status == 'approved':
            approval_status = WorkflowService.get_approval_status(wr)
            if approval_status['is_satisfied']:
                # Find next stage
                next_transitions = WorkflowTransition.objects.filter(
                    workflow=wr.workflow,
                    from_stage=wr.current_stage,
                    is_rejection=False,
                ).order_by('to_stage__sequence')

                if next_transitions.exists():
                    next_stage = next_transitions.first().to_stage
                    logger.info(
                        f"Auto-advancing {wr.content_object} to '{next_stage.name}'"
                    )
                    WorkflowService.transition(
                        workflow_record=wr,
                        to_stage_slug=next_stage.slug,
                        user=user,
                        comments=f"Auto-advanced after all approvals received",
                        ip_address=ip_address,
                    )

        return approval_request

    @staticmethod
    @transaction.atomic
    def extend_deadline(workflow_record, days, reason, user, ip_address=None):
        """
        Extend the SLA deadline for the current stage.

        Args:
            workflow_record: The WorkflowRecord
            days: Number of days to extend by
            reason: Reason for extension
            user: User requesting extension
            ip_address: Client IP
        """
        old_deadline = workflow_record.estimated_exit_date
        if old_deadline:
            new_deadline = old_deadline + timedelta(days=days)
        else:
            new_deadline = timezone.now() + timedelta(days=days)

        workflow_record.estimated_exit_date = new_deadline
        workflow_record.is_overdue = False
        workflow_record.save(update_fields=['estimated_exit_date', 'is_overdue'])

        # Audit log
        AuditLog.objects.create(
            content_type=workflow_record.content_type,
            object_id=workflow_record.object_id,
            object_repr=str(workflow_record.content_object),
            user=user,
            action='update',
            ip_address=ip_address,
            old_values={
                'estimated_exit_date': old_deadline.isoformat() if old_deadline else None
            },
            new_values={
                'estimated_exit_date': new_deadline.isoformat(),
                'extension_days': days,
                'extension_reason': reason,
            },
            change_summary=f"Deadline extended by {days} days. Reason: {reason}",
        )

        logger.info(
            f"Deadline extended: {workflow_record.content_object} +{days} days by {user}"
        )

    @staticmethod
    def get_records_pending_action(user):
        """
        Get all workflow records where the user has pending actions.
        (approval requests, owned records in active stages, etc.)

        Returns:
            QuerySet of WorkflowApprovalRequest where status='pending' for this user
        """
        return WorkflowApprovalRequest.objects.filter(
            approver=user,
            status='pending',
        ).select_related(
            'gate', 'gate__stage', 'workflow_record', 'workflow_record__workflow'
        )

    @staticmethod
    def get_overdue_records():
        """Return all active workflow records that have exceeded their SLA."""
        return WorkflowRecord.objects.filter(
            is_active=True,
            estimated_exit_date__lt=timezone.now(),
        ).select_related('current_stage', 'workflow')

    @staticmethod
    def _create_approval_requests(workflow_record, stage):
        """
        Create approval requests for all gates at a stage.
        Internal method — called during transition.
        """
        gates = WorkflowApprovalGate.objects.filter(stage=stage)
        for gate in gates:
            # In a real system, you'd look up users with the required role.
            # For now, we create the gate structure and approvers are assigned
            # via the API (add_approver endpoint).
            logger.info(
                f"Approval gate '{gate.name}' created for "
                f"{workflow_record.content_object} at stage '{stage.name}'"
            )

    @staticmethod
    def add_approver(workflow_record, gate_id, approver_user):
        """
        Add a specific user as an approver for a gate.

        Args:
            workflow_record: The WorkflowRecord
            gate_id: ID of the WorkflowApprovalGate
            approver_user: User to add as approver
        """
        gate = WorkflowApprovalGate.objects.get(id=gate_id)
        if gate.stage != workflow_record.current_stage:
            raise WorkflowError(
                "Cannot add approver to a gate that is not in the current stage"
            )

        due_date = None
        if gate.estimated_response_days:
            due_date = timezone.now() + timedelta(days=gate.estimated_response_days)

        request, created = WorkflowApprovalRequest.objects.get_or_create(
            gate=gate,
            workflow_record=workflow_record,
            approver=approver_user,
            defaults={
                'due_date': due_date,
            }
        )
        return request, created
