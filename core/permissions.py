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
