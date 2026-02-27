"""
Finite State Machine for Document Lifecycle Management.

Defines valid state transitions for the 9-state document lifecycle:
Draft → In Review → Approved → Training Period → Effective → Superseded/Obsolete/Archived
                                                           → Cancelled (from draft/in_review)
"""
from django.core.exceptions import ValidationError

# Valid state transitions map
VALID_TRANSITIONS = {
    'draft': ['in_review', 'cancelled'],
    'in_review': ['approved', 'draft', 'cancelled'],  # draft = rejection back to draft
    'approved': ['training_period', 'effective'],  # effective if no training required
    'training_period': ['effective'],
    'effective': ['superseded', 'obsolete', 'archived', 'in_review'],  # in_review = periodic review revision
    'superseded': ['archived'],
    'obsolete': ['archived'],
    'archived': [],  # terminal state
    'cancelled': [],  # terminal state
}

# Permissions required for each transition
TRANSITION_PERMISSIONS = {
    ('draft', 'in_review'): 'author',  # Author submits for review
    ('draft', 'cancelled'): 'author_or_admin',
    ('in_review', 'approved'): 'approver',  # All approvers must approve
    ('in_review', 'draft'): 'reviewer',  # Rejection sends back to draft
    ('in_review', 'cancelled'): 'admin',
    ('approved', 'training_period'): 'system',  # Auto-transition if training required
    ('approved', 'effective'): 'system_or_admin',  # Auto if no training, or admin override
    ('training_period', 'effective'): 'system',  # Auto when training complete
    ('effective', 'superseded'): 'admin',
    ('effective', 'obsolete'): 'admin',
    ('effective', 'archived'): 'admin',
    ('effective', 'in_review'): 'author_or_admin',  # Periodic review / revision
    ('superseded', 'archived'): 'admin',
    ('obsolete', 'archived'): 'admin',
}

# Human-readable transition labels
TRANSITION_LABELS = {
    ('draft', 'in_review'): 'Submit for Review',
    ('draft', 'cancelled'): 'Cancel Document',
    ('in_review', 'approved'): 'Approve',
    ('in_review', 'draft'): 'Reject / Return to Draft',
    ('in_review', 'cancelled'): 'Cancel Document',
    ('approved', 'training_period'): 'Begin Training Period',
    ('approved', 'effective'): 'Make Effective',
    ('training_period', 'effective'): 'Training Complete - Make Effective',
    ('effective', 'superseded'): 'Supersede',
    ('effective', 'obsolete'): 'Make Obsolete',
    ('effective', 'archived'): 'Archive',
    ('effective', 'in_review'): 'Initiate Revision',
    ('superseded', 'archived'): 'Archive',
    ('obsolete', 'archived'): 'Archive',
}


def validate_transition(current_state, target_state):
    """
    Validate that a state transition is allowed.

    Args:
        current_state: Current vault_state of the document
        target_state: Desired target vault_state

    Returns:
        bool: True if transition is valid

    Raises:
        ValidationError: If transition is not allowed
    """
    if current_state not in VALID_TRANSITIONS:
        raise ValidationError(f"Unknown current state: '{current_state}'")

    valid_targets = VALID_TRANSITIONS[current_state]
    if target_state not in valid_targets:
        valid_str = ', '.join(valid_targets) if valid_targets else 'none (terminal state)'
        raise ValidationError(
            f"Invalid transition from '{current_state}' to '{target_state}'. "
            f"Valid transitions from '{current_state}': {valid_str}"
        )
    return True


def get_available_transitions(current_state):
    """
    Get list of available transitions from current state.

    Returns:
        list of dicts with target_state, label, permission_required
    """
    targets = VALID_TRANSITIONS.get(current_state, [])
    result = []
    for target in targets:
        result.append({
            'target_state': target,
            'label': TRANSITION_LABELS.get((current_state, target), f'Move to {target}'),
            'permission_required': TRANSITION_PERMISSIONS.get((current_state, target), 'admin'),
        })
    return result


def check_transition_permission(current_state, target_state, user, document):
    """
    Check if user has permission to perform a specific transition.

    Returns:
        tuple: (allowed: bool, reason: str)
    """
    perm = TRANSITION_PERMISSIONS.get((current_state, target_state), 'admin')

    if perm == 'system':
        return True, 'System transition'

    if perm == 'author':
        if document.owner == user or document.created_by == user:
            return True, 'Author permission'
        return False, 'Only the document author/owner can perform this action'

    if perm == 'author_or_admin':
        if document.owner == user or document.created_by == user or user.is_staff:
            return True, 'Author or admin permission'
        return False, 'Only the document author/owner or admin can perform this action'

    if perm == 'reviewer':
        is_approver = document.approvers.filter(approver=user).exists()
        if is_approver or user.is_staff:
            return True, 'Reviewer permission'
        return False, 'Only assigned reviewers can reject documents'

    if perm == 'approver':
        # Check if user is an assigned approver
        is_approver = document.approvers.filter(approver=user).exists()
        if is_approver:
            return True, 'Approver permission'
        if user.is_staff:
            return True, 'Admin override'
        return False, 'Only assigned approvers can approve documents'

    if perm == 'system_or_admin':
        if user.is_staff:
            return True, 'Admin permission'
        return False, 'Only system or admin can perform this action'

    if perm == 'admin':
        if user.is_staff:
            return True, 'Admin permission'
        return False, 'Only administrators can perform this action'

    return False, f'Unknown permission type: {perm}'
