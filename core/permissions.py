"""Custom permission classes for role-based access control."""
from rest_framework.permissions import BasePermission


class IsQualityDirector(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'profile') and \
            request.user.profile.roles.filter(name='quality_director').exists()


class CanApproveDocuments(BasePermission):
    def has_permission(self, request, view):
        if not hasattr(request.user, 'profile'):
            return False
        return request.user.profile.roles.filter(can_approve_documents=True).exists()


class CanSignDocuments(BasePermission):
    def has_permission(self, request, view):
        if not hasattr(request.user, 'profile'):
            return False
        return request.user.profile.roles.filter(can_sign_documents=True).exists()


class CanCreateCAPA(BasePermission):
    def has_permission(self, request, view):
        if not hasattr(request.user, 'profile'):
            return False
        return request.user.profile.roles.filter(can_create_capa=True).exists()


class CanCloseCAPA(BasePermission):
    def has_permission(self, request, view):
        if not hasattr(request.user, 'profile'):
            return False
        return request.user.profile.roles.filter(can_close_capa=True).exists()


class CanViewAuditTrail(BasePermission):
    def has_permission(self, request, view):
        if not hasattr(request.user, 'profile'):
            return False
        return request.user.profile.roles.filter(can_view_audit_trail=True).exists()


class TrainingGatePermission(BasePermission):
    """
    Blocks access to document content if user hasn't completed required training.
    Only applies to documents in 'effective' state with requires_training=True.
    """
    def has_object_permission(self, request, view, obj):
        # Only gate effective documents that require training
        if not hasattr(obj, 'vault_state') or obj.vault_state != 'effective':
            return True
        if not getattr(obj, 'requires_training', False):
            return True

        # Check if user has acknowledged
        from documents.models import DocumentAcknowledgment
        return DocumentAcknowledgment.objects.filter(
            document=obj, user=request.user
        ).exists()
