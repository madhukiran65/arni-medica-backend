"""
Seed workflow definitions for all EQMS modules.
Run via: python manage.py shell < workflows/seed_data.py
Or call seed_all_workflows() from a data migration.
"""
from workflows.models import (
    WorkflowDefinition, WorkflowStage, WorkflowTransition,
    WorkflowApprovalGate,
)


def seed_all_workflows():
    """Create all standard EQMS workflow definitions."""
    seed_document_workflow()
    seed_capa_workflow()
    seed_deviation_workflow()
    seed_complaint_workflow()
    seed_change_control_workflow()
    print("All workflow definitions seeded successfully.")


def seed_document_workflow():
    """
    Document Lifecycle: 7 stages
    Draft → InReview → ReviewValidation → SignOff → Released → Obsolete → Archived
    """
    wf, created = WorkflowDefinition.objects.get_or_create(
        name='Document Lifecycle',
        model_type='document',
        defaults={'description': 'Standard document lifecycle workflow (7 stages)'}
    )
    if not created:
        print("Document workflow already exists, skipping.")
        return

    stages_data = [
        {'name': 'Draft', 'slug': 'draft', 'sequence': 1, 'is_initial': True,
         'allows_edit': True, 'color': '#9CA3AF', 'sla_days': None},
        {'name': 'In Review', 'slug': 'in-review', 'sequence': 2,
         'requires_approval': True, 'required_approvers_count': 1,
         'allows_edit': False, 'color': '#3B82F6', 'sla_days': 14},
        {'name': 'Review Validation', 'slug': 'review-validation', 'sequence': 3,
         'requires_approval': True, 'required_approvers_count': 1,
         'allows_edit': False, 'color': '#8B5CF6', 'sla_days': 7},
        {'name': 'Sign-Off', 'slug': 'sign-off', 'sequence': 4,
         'requires_signature': True, 'signature_reason': 'approval',
         'allows_edit': False, 'color': '#F59E0B', 'sla_days': 5},
        {'name': 'Released', 'slug': 'released', 'sequence': 5,
         'allows_edit': False, 'color': '#10B981', 'sla_days': None},
        {'name': 'Obsolete', 'slug': 'obsolete', 'sequence': 6,
         'allows_edit': False, 'is_terminal': True, 'color': '#EF4444'},
        {'name': 'Archived', 'slug': 'archived', 'sequence': 7,
         'allows_edit': False, 'is_terminal': True, 'color': '#6B7280'},
    ]
    stages = {}
    for s in stages_data:
        stage = WorkflowStage.objects.create(workflow=wf, **s)
        stages[s['slug']] = stage

    # Transitions
    transitions = [
        ('draft', 'in-review', 'Submit for Review'),
        ('in-review', 'review-validation', 'Validate Review'),
        ('in-review', 'draft', 'Return to Draft'),
        ('review-validation', 'sign-off', 'Request Sign-Off'),
        ('review-validation', 'in-review', 'Return to Review'),
        ('sign-off', 'released', 'Release Document'),
        ('sign-off', 'review-validation', 'Return for Validation'),
        ('released', 'obsolete', 'Mark Obsolete'),
        ('released', 'archived', 'Archive Document'),
        ('obsolete', 'archived', 'Archive'),
    ]
    for from_slug, to_slug, label in transitions:
        is_rejection = 'Return' in label
        WorkflowTransition.objects.create(
            workflow=wf,
            from_stage=stages[from_slug],
            to_stage=stages[to_slug],
            label=label,
            is_rejection=is_rejection,
            button_color='#EF4444' if is_rejection else '#3B82F6',
        )

    # Approval gates
    WorkflowApprovalGate.objects.create(
        stage=stages['in-review'], name='Document Reviewer',
        required_role='document_reviewer', required_count=1,
        approval_mode='all', sequence=1, estimated_response_days=7,
    )
    WorkflowApprovalGate.objects.create(
        stage=stages['review-validation'], name='QA Validator',
        required_role='qa_validator', required_count=1,
        approval_mode='all', sequence=1, estimated_response_days=5,
    )

    print(f"Document workflow created: {len(stages)} stages, {len(transitions)} transitions")


def seed_capa_workflow():
    """
    CAPA Lifecycle: 5 phases
    Investigation → Root Cause → Risk Affirmation → CAPA Plan → Closure
    """
    wf, created = WorkflowDefinition.objects.get_or_create(
        name='CAPA Lifecycle',
        model_type='capa',
        defaults={'description': 'CAPA 5-phase lifecycle with gate validation'}
    )
    if not created:
        print("CAPA workflow already exists, skipping.")
        return

    stages_data = [
        {'name': 'Investigation', 'slug': 'investigation', 'sequence': 1,
         'is_initial': True, 'allows_edit': True, 'color': '#3B82F6',
         'sla_days': 30,
         'required_fields': ['what_happened', 'when_happened', 'where_happened']},
        {'name': 'Root Cause Analysis', 'slug': 'root-cause', 'sequence': 2,
         'allows_edit': True, 'color': '#8B5CF6', 'sla_days': 21,
         'required_fields': ['root_cause', 'root_cause_analysis_method'],
         'requires_approval': True, 'required_approvers_count': 1},
        {'name': 'Risk Affirmation', 'slug': 'risk-affirmation', 'sequence': 3,
         'allows_edit': True, 'color': '#F59E0B', 'sla_days': 14,
         'required_fields': ['risk_severity', 'risk_occurrence'],
         'requires_signature': True, 'signature_reason': 'approval'},
        {'name': 'CAPA Plan', 'slug': 'capa-plan', 'sequence': 4,
         'allows_edit': True, 'color': '#EC4899', 'sla_days': 30,
         'requires_approval': True, 'required_approvers_count': 2,
         'requires_signature': True, 'signature_reason': 'approval'},
        {'name': 'Closure', 'slug': 'closure', 'sequence': 5,
         'allows_edit': True, 'color': '#10B981', 'is_terminal': True,
         'required_fields': ['effectiveness_confirmed'],
         'requires_signature': True, 'signature_reason': 'capa_closure'},
    ]
    stages = {}
    for s in stages_data:
        stage = WorkflowStage.objects.create(workflow=wf, **s)
        stages[s['slug']] = stage

    transitions = [
        ('investigation', 'root-cause', 'Submit Root Cause Analysis'),
        ('root-cause', 'risk-affirmation', 'Submit Risk Assessment'),
        ('root-cause', 'investigation', 'Return to Investigation'),
        ('risk-affirmation', 'capa-plan', 'Submit CAPA Plan'),
        ('risk-affirmation', 'root-cause', 'Revise Root Cause'),
        ('capa-plan', 'closure', 'Submit for Closure'),
        ('capa-plan', 'risk-affirmation', 'Revise Risk Assessment'),
    ]
    for from_slug, to_slug, label in transitions:
        is_rejection = 'Return' in label or 'Revise' in label
        WorkflowTransition.objects.create(
            workflow=wf,
            from_stage=stages[from_slug],
            to_stage=stages[to_slug],
            label=label,
            is_rejection=is_rejection,
            button_color='#EF4444' if is_rejection else '#3B82F6',
        )

    # Approval gates
    WorkflowApprovalGate.objects.create(
        stage=stages['root-cause'], name='QA Lead Review',
        required_role='qa_lead', required_count=1,
        approval_mode='all', sequence=1, estimated_response_days=5,
    )
    WorkflowApprovalGate.objects.create(
        stage=stages['capa-plan'], name='Management Approval',
        required_role='manager', required_count=2,
        approval_mode='count', sequence=1, estimated_response_days=7,
    )
    WorkflowApprovalGate.objects.create(
        stage=stages['capa-plan'], name='Review Board',
        required_role='review_board', required_count=1,
        approval_mode='all', sequence=2, estimated_response_days=5,
    )

    print(f"CAPA workflow created: {len(stages)} stages, {len(transitions)} transitions")


def seed_deviation_workflow():
    """
    Deviation Workflow: 8 stages
    Opened → QA Review → Investigation → CAPA Plan →
    Pending CAPA Approval → Pending CAPA Completion → Pending Final Approval → Completed
    """
    wf, created = WorkflowDefinition.objects.get_or_create(
        name='Deviation Workflow',
        model_type='deviation',
        defaults={'description': 'Deviation 8-stage workflow with QA gates'}
    )
    if not created:
        print("Deviation workflow already exists, skipping.")
        return

    stages_data = [
        {'name': 'Opened', 'slug': 'opened', 'sequence': 1,
         'is_initial': True, 'allows_edit': True, 'color': '#9CA3AF', 'sla_days': 3},
        {'name': 'QA Review', 'slug': 'qa-review', 'sequence': 2,
         'requires_approval': True, 'required_approvers_count': 1,
         'allows_edit': False, 'color': '#3B82F6', 'sla_days': 5},
        {'name': 'Investigation', 'slug': 'investigation', 'sequence': 3,
         'allows_edit': True, 'color': '#8B5CF6', 'sla_days': 21},
        {'name': 'CAPA Plan', 'slug': 'capa-plan', 'sequence': 4,
         'allows_edit': True, 'color': '#F59E0B', 'sla_days': 14},
        {'name': 'Pending CAPA Approval', 'slug': 'pending-capa-approval', 'sequence': 5,
         'requires_approval': True, 'required_approvers_count': 1,
         'requires_signature': True, 'signature_reason': 'approval',
         'allows_edit': False, 'color': '#EC4899', 'sla_days': 7},
        {'name': 'Pending CAPA Completion', 'slug': 'pending-capa-completion', 'sequence': 6,
         'allows_edit': True, 'color': '#14B8A6', 'sla_days': 60},
        {'name': 'Pending Final Approval', 'slug': 'pending-final-approval', 'sequence': 7,
         'requires_approval': True, 'required_approvers_count': 1,
         'requires_signature': True, 'signature_reason': 'approval',
         'allows_edit': False, 'color': '#F97316', 'sla_days': 7},
        {'name': 'Completed', 'slug': 'completed', 'sequence': 8,
         'is_terminal': True, 'allows_edit': False, 'color': '#10B981'},
    ]
    stages = {}
    for s in stages_data:
        stage = WorkflowStage.objects.create(workflow=wf, **s)
        stages[s['slug']] = stage

    transitions = [
        ('opened', 'qa-review', 'Submit for QA Review'),
        ('qa-review', 'investigation', 'Approve for Investigation'),
        ('qa-review', 'opened', 'Return to Originator'),
        ('investigation', 'capa-plan', 'Submit CAPA Plan'),
        ('investigation', 'qa-review', 'Return for QA Review'),
        ('capa-plan', 'pending-capa-approval', 'Submit for CAPA Approval'),
        ('pending-capa-approval', 'pending-capa-completion', 'Approve CAPA Plan'),
        ('pending-capa-approval', 'capa-plan', 'Reject CAPA Plan'),
        ('pending-capa-completion', 'pending-final-approval', 'Submit for Final Approval'),
        ('pending-final-approval', 'completed', 'Complete Deviation'),
        ('pending-final-approval', 'pending-capa-completion', 'Reject Final'),
    ]
    for from_slug, to_slug, label in transitions:
        is_rejection = 'Return' in label or 'Reject' in label
        WorkflowTransition.objects.create(
            workflow=wf,
            from_stage=stages[from_slug],
            to_stage=stages[to_slug],
            label=label,
            is_rejection=is_rejection,
            button_color='#EF4444' if is_rejection else '#3B82F6',
        )

    print(f"Deviation workflow created: {len(stages)} stages, {len(transitions)} transitions")


def seed_complaint_workflow():
    """
    Complaint Workflow: 5 stages
    New → Under Investigation → CAPA Initiated → Investigation Complete → Closed
    """
    wf, created = WorkflowDefinition.objects.get_or_create(
        name='Complaint Workflow',
        model_type='complaint',
        defaults={'description': 'Complaint handling workflow with MDR integration'}
    )
    if not created:
        print("Complaint workflow already exists, skipping.")
        return

    stages_data = [
        {'name': 'New', 'slug': 'new', 'sequence': 1,
         'is_initial': True, 'allows_edit': True, 'color': '#9CA3AF', 'sla_days': 3},
        {'name': 'Under Investigation', 'slug': 'under-investigation', 'sequence': 2,
         'allows_edit': True, 'color': '#3B82F6', 'sla_days': 30},
        {'name': 'CAPA Initiated', 'slug': 'capa-initiated', 'sequence': 3,
         'allows_edit': True, 'color': '#F59E0B', 'sla_days': 14},
        {'name': 'Investigation Complete', 'slug': 'investigation-complete', 'sequence': 4,
         'requires_approval': True, 'required_approvers_count': 1,
         'requires_signature': True, 'signature_reason': 'complaint_closure',
         'allows_edit': False, 'color': '#10B981', 'sla_days': 7},
        {'name': 'Closed', 'slug': 'closed', 'sequence': 5,
         'is_terminal': True, 'allows_edit': False, 'color': '#6B7280'},
    ]
    stages = {}
    for s in stages_data:
        stage = WorkflowStage.objects.create(workflow=wf, **s)
        stages[s['slug']] = stage

    transitions = [
        ('new', 'under-investigation', 'Begin Investigation'),
        ('under-investigation', 'capa-initiated', 'Initiate CAPA'),
        ('under-investigation', 'investigation-complete', 'Complete Investigation'),
        ('capa-initiated', 'investigation-complete', 'Complete Investigation'),
        ('investigation-complete', 'closed', 'Close Complaint'),
        ('investigation-complete', 'under-investigation', 'Reopen Investigation'),
    ]
    for from_slug, to_slug, label in transitions:
        is_rejection = 'Reopen' in label
        WorkflowTransition.objects.create(
            workflow=wf,
            from_stage=stages[from_slug],
            to_stage=stages[to_slug],
            label=label,
            is_rejection=is_rejection,
            button_color='#EF4444' if is_rejection else '#3B82F6',
        )

    print(f"Complaint workflow created: {len(stages)} stages, {len(transitions)} transitions")


def seed_change_control_workflow():
    """
    Change Control Workflow: 7 stages
    Submitted → Screening → Impact Assessment → Approval →
    Implementation → Verification → Closed
    """
    wf, created = WorkflowDefinition.objects.get_or_create(
        name='Change Control Workflow',
        model_type='change_control',
        defaults={'description': 'Change control 7-stage workflow'}
    )
    if not created:
        print("Change Control workflow already exists, skipping.")
        return

    stages_data = [
        {'name': 'Submitted', 'slug': 'submitted', 'sequence': 1,
         'is_initial': True, 'allows_edit': True, 'color': '#9CA3AF', 'sla_days': 3},
        {'name': 'Screening', 'slug': 'screening', 'sequence': 2,
         'requires_approval': True, 'required_approvers_count': 1,
         'allows_edit': False, 'color': '#3B82F6', 'sla_days': 5},
        {'name': 'Impact Assessment', 'slug': 'impact-assessment', 'sequence': 3,
         'allows_edit': True, 'color': '#8B5CF6', 'sla_days': 14},
        {'name': 'Approval', 'slug': 'approval', 'sequence': 4,
         'requires_approval': True, 'required_approvers_count': 2,
         'requires_signature': True, 'signature_reason': 'change_approval',
         'allows_edit': False, 'color': '#F59E0B', 'sla_days': 7},
        {'name': 'Implementation', 'slug': 'implementation', 'sequence': 5,
         'allows_edit': True, 'color': '#EC4899', 'sla_days': 60},
        {'name': 'Verification', 'slug': 'verification', 'sequence': 6,
         'requires_signature': True, 'signature_reason': 'change_approval',
         'allows_edit': False, 'color': '#14B8A6', 'sla_days': 14},
        {'name': 'Closed', 'slug': 'closed', 'sequence': 7,
         'is_terminal': True, 'allows_edit': False, 'color': '#10B981'},
    ]
    stages = {}
    for s in stages_data:
        stage = WorkflowStage.objects.create(workflow=wf, **s)
        stages[s['slug']] = stage

    transitions = [
        ('submitted', 'screening', 'Submit for Screening'),
        ('screening', 'impact-assessment', 'Approve for Assessment'),
        ('screening', 'submitted', 'Return to Submitter'),
        ('impact-assessment', 'approval', 'Submit for Approval'),
        ('impact-assessment', 'screening', 'Return for Re-screening'),
        ('approval', 'implementation', 'Approve for Implementation'),
        ('approval', 'impact-assessment', 'Reject - Reassess'),
        ('implementation', 'verification', 'Submit for Verification'),
        ('verification', 'closed', 'Close Change Control'),
        ('verification', 'implementation', 'Return for Rework'),
    ]
    for from_slug, to_slug, label in transitions:
        is_rejection = 'Return' in label or 'Reject' in label
        WorkflowTransition.objects.create(
            workflow=wf,
            from_stage=stages[from_slug],
            to_stage=stages[to_slug],
            label=label,
            is_rejection=is_rejection,
            button_color='#EF4444' if is_rejection else '#3B82F6',
        )

    print(f"Change Control workflow created: {len(stages)} stages, {len(transitions)} transitions")


if __name__ == '__main__':
    seed_all_workflows()
