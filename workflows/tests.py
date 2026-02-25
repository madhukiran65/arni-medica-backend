"""
Workflow Engine Tests.
Tests core workflow transitions, approval gates, and validation.
"""
from datetime import timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from core.models import AuditLog
from .models import (
    WorkflowDefinition, WorkflowStage, WorkflowTransition,
    WorkflowRecord, WorkflowHistory, WorkflowApprovalGate,
    WorkflowApprovalRequest,
)
from .services import (
    WorkflowService, TransitionNotAllowed, ApprovalRequired,
    FieldValidationError, SignatureRequired,
)

User = get_user_model()


class WorkflowEngineTestCase(TestCase):
    """Test the core workflow engine."""

    def setUp(self):
        """Create a test workflow with 3 stages and transitions."""
        self.user = User.objects.create_user(
            username='testuser', password='TestPass1234!', email='test@example.com'
        )
        self.approver = User.objects.create_user(
            username='approver', password='TestPass1234!', email='approver@example.com'
        )

        # Create workflow definition
        self.workflow = WorkflowDefinition.objects.create(
            name='Test Workflow',
            model_type='test',
            description='Test workflow for unit tests',
        )

        # Create stages
        self.stage_draft = WorkflowStage.objects.create(
            workflow=self.workflow, name='Draft', slug='draft',
            sequence=1, is_initial=True, allows_edit=True,
        )
        self.stage_review = WorkflowStage.objects.create(
            workflow=self.workflow, name='In Review', slug='in-review',
            sequence=2, requires_approval=True, required_approvers_count=1,
        )
        self.stage_approved = WorkflowStage.objects.create(
            workflow=self.workflow, name='Approved', slug='approved',
            sequence=3, requires_signature=True, signature_reason='approval',
            is_terminal=True, allows_edit=False,
        )

        # Create transitions
        WorkflowTransition.objects.create(
            workflow=self.workflow,
            from_stage=self.stage_draft, to_stage=self.stage_review,
            label='Submit for Review',
        )
        WorkflowTransition.objects.create(
            workflow=self.workflow,
            from_stage=self.stage_review, to_stage=self.stage_approved,
            label='Approve',
        )
        WorkflowTransition.objects.create(
            workflow=self.workflow,
            from_stage=self.stage_review, to_stage=self.stage_draft,
            label='Reject', is_rejection=True,
        )

        # Create approval gate for review stage
        self.approval_gate = WorkflowApprovalGate.objects.create(
            stage=self.stage_review,
            name='Review Gate',
            required_role='reviewer',
            required_count=1,
            approval_mode='all',
        )

    def _create_workflow_record(self):
        """Helper to create a workflow record using AuditLog as a test model."""
        # Use User as our test content type (any model will do)
        ct = ContentType.objects.get_for_model(User)
        return WorkflowRecord.objects.create(
            workflow=self.workflow,
            current_stage=self.stage_draft,
            content_type=ct,
            object_id=str(self.user.pk),
        )

    def test_initialize_workflow(self):
        """Test workflow initialization."""
        record = WorkflowService.initialize_workflow(
            record=self.user,
            workflow_name='Test Workflow',
            model_type='test',
            user=self.user,
        )
        self.assertEqual(record.current_stage, self.stage_draft)
        self.assertTrue(record.is_active)

    def test_valid_transition(self):
        """Test a legal transition (Draft → In Review)."""
        wr = self._create_workflow_record()
        updated = WorkflowService.transition(
            workflow_record=wr,
            to_stage_slug='in-review',
            user=self.user,
            comments='Ready for review',
        )
        self.assertEqual(updated.current_stage, self.stage_review)

    def test_invalid_transition(self):
        """Test an illegal transition (Draft → Approved directly)."""
        wr = self._create_workflow_record()
        with self.assertRaises(TransitionNotAllowed):
            WorkflowService.transition(
                workflow_record=wr,
                to_stage_slug='approved',
                user=self.user,
            )

    def test_approval_flow(self):
        """Test that approval gates are enforced."""
        wr = self._create_workflow_record()

        # Move to review
        WorkflowService.transition(wr, 'in-review', self.user)

        # Add approver
        req, created = WorkflowService.add_approver(wr, self.approval_gate.id, self.approver)
        self.assertTrue(created)
        self.assertEqual(req.status, 'pending')

        # Try to advance without approval — should fail
        with self.assertRaises(ApprovalRequired):
            WorkflowService.transition(wr, 'approved', self.user,
                                       signature_password='TestPass1234!')

        # Approve
        WorkflowService.respond_to_approval(
            approval_request=req,
            status='approved',
            user=self.approver,
            comments='Looks good',
        )

        # Now transition should work (with signature)
        updated = WorkflowService.transition(
            wr, 'approved', self.user,
            signature_password='TestPass1234!',
        )
        self.assertEqual(updated.current_stage, self.stage_approved)

    def test_history_is_immutable(self):
        """Test that workflow history records cannot be modified."""
        wr = self._create_workflow_record()
        WorkflowService.transition(wr, 'in-review', self.user)

        history = WorkflowHistory.objects.first()
        with self.assertRaises(ValueError):
            history.comments = 'Trying to modify'
            history.save()

    def test_audit_log_created_on_transition(self):
        """Test that AuditLog entries are created on transitions."""
        wr = self._create_workflow_record()
        initial_count = AuditLog.objects.count()

        WorkflowService.transition(wr, 'in-review', self.user)

        self.assertGreater(AuditLog.objects.count(), initial_count)

    def test_get_valid_transitions(self):
        """Test getting valid next states."""
        wr = self._create_workflow_record()
        transitions = WorkflowService.get_valid_transitions(wr)

        # From Draft, should only be able to go to In Review
        self.assertEqual(len(transitions), 1)
        self.assertEqual(transitions[0]['stage_slug'], 'in-review')

    def test_extend_deadline(self):
        """Test deadline extension."""
        wr = self._create_workflow_record()
        wr.estimated_exit_date = timezone.now() + timedelta(days=5)
        wr.save()

        WorkflowService.extend_deadline(
            wr, days=10, reason='Need more time', user=self.user
        )
        wr.refresh_from_db()
        self.assertFalse(wr.is_overdue)

    def test_rejection_flow(self):
        """Test rejection transition (In Review → Draft)."""
        wr = self._create_workflow_record()
        WorkflowService.transition(wr, 'in-review', self.user)

        # Add approver and reject
        req, _ = WorkflowService.add_approver(wr, self.approval_gate.id, self.approver)
        WorkflowService.respond_to_approval(req, 'rejected', self.approver, 'Needs rework')

        # Move back to draft
        updated = WorkflowService.transition(
            wr, 'draft', self.user, comments='Reworking based on feedback'
        )
        self.assertEqual(updated.current_stage, self.stage_draft)
