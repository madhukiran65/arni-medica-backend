from rest_framework import viewsets, status, decorators
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password
from django.utils import timezone
import hashlib

from documents.models import (
    Document,
    DocumentVersion,
    DocumentChangeOrder,
    DocumentChangeApproval,
)
from documents.serializers import (
    DocumentSerializer,
    DocumentVersionSerializer,
    DocumentChangeOrderSerializer,
    DocumentChangeApprovalSerializer,
)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing documents with CRUD operations, signing, versioning, and audit trails.
    
    Actions:
    - list: Get all documents
    - create: Create a new document
    - retrieve: Get a specific document
    - update: Update a document
    - partial_update: Partially update a document
    - destroy: Delete a document
    - sign: Sign a document electronically
    - versions: Get version history of a document
    - audit_trail: Get audit trail of a document
    """
    
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'document_type', 'department']
    search_fields = ['document_id', 'title', 'description']
    ordering_fields = ['created_at', 'document_id', 'status']
    ordering = ['-created_at']
    
    @decorators.action(detail=True, methods=['post'])
    def sign(self, request, pk=None):
        """
        Sign a document electronically.
        
        Requires:
        - password: User's password for verification
        - reason: Reason for signing
        
        Returns:
        - 200: Document signed successfully
        - 400: Invalid password or missing fields
        - 404: Document not found
        """
        document = self.get_object()
        password = request.data.get('password')
        reason = request.data.get('reason')
        
        if not password or not reason:
            return Response(
                {'error': 'password and reason are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify password
        if not check_password(password, request.user.password):
            return Response(
                {'error': 'Invalid password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create electronic signature
        signature_data = f"{document.id}:{request.user.id}:{timezone.now()}:{reason}"
        signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()
        
        # Update document status
        if document.status == 'pending_approval':
            document.status = 'approved'
            document.save()
        
        return Response({
            'success': True,
            'message': 'Document signed successfully',
            'signature_hash': signature_hash,
            'signed_by': request.user.username,
            'signed_at': timezone.now().isoformat(),
            'document': DocumentSerializer(document).data,
        })
    
    @decorators.action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """
        Get version history of a document.
        
        Returns:
        - 200: List of document versions
        - 404: Document not found
        """
        document = self.get_object()
        versions = document.versions.all()
        serializer = DocumentVersionSerializer(versions, many=True)
        return Response(serializer.data)
    
    @decorators.action(detail=True, methods=['get'])
    def audit_trail(self, request, pk=None):
        """
        Get audit trail of a document.
        
        Returns:
        - 200: Audit trail information
        - 404: Document not found
        """
        document = self.get_object()
        return Response({
            'document_id': document.document_id,
            'created_at': document.created_at,
            'created_by': document.created_by.username if document.created_by else None,
            'updated_at': document.updated_at,
            'updated_by': document.updated_by.username if document.updated_by else None,
            'status': document.status,
            'revision_number': document.revision_number,
            'version': document.version,
            'audit_note': document.audit_note,
        })


class DocumentChangeOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing document change orders.
    
    Actions:
    - list: Get all change orders
    - create: Create a new change order
    - retrieve: Get a specific change order
    - update: Update a change order
    - partial_update: Partially update a change order
    - destroy: Delete a change order
    - approve: Approve a change order
    """
    
    queryset = DocumentChangeOrder.objects.all()
    serializer_class = DocumentChangeOrderSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'change_type']
    search_fields = ['dco_number', 'title', 'reason']
    ordering_fields = ['created_at', 'dco_number', 'status']
    ordering = ['-created_at']
    
    @decorators.action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve a document change order.
        
        Requires:
        - comments (optional): Comments for approval
        - password: User's password for verification
        
        Returns:
        - 200: Change order approved successfully
        - 400: Invalid password or validation error
        - 404: Change order not found
        """
        dco = self.get_object()
        password = request.data.get('password')
        comments = request.data.get('comments', '')
        
        if not password:
            return Response(
                {'error': 'password is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify password
        if not check_password(password, request.user.password):
            return Response(
                {'error': 'Invalid password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create signature hash
        signature_data = f"{dco.id}:{request.user.id}:{timezone.now()}"
        signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()
        
        # Create or update approval
        approval, created = DocumentChangeApproval.objects.get_or_create(
            dco=dco,
            approver=request.user,
            defaults={
                'status': 'approved',
                'comments': comments,
                'signature_hash': signature_hash,
                'approved_at': timezone.now(),
            }
        )
        
        if not created:
            approval.status = 'approved'
            approval.comments = comments
            approval.signature_hash = signature_hash
            approval.approved_at = timezone.now()
            approval.save()
        
        # Update DCO status if all required approvals are done
        if dco.status == 'under_review':
            dco.status = 'approved'
            dco.save()
        
        serializer = DocumentChangeApprovalSerializer(approval)
        return Response({
            'success': True,
            'message': 'Change order approved successfully',
            'approval': serializer.data,
        })
