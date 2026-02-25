from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404

from .models import (
    DocumentInfocardType,
    Document,
    DocumentCheckout,
    DocumentChangeOrder,
    DocumentSnapshot,
    DocumentVersion,
    DocumentApprover,
)
from .serializers import (
    DocumentInfocardTypeSerializer,
    DocumentListSerializer,
    DocumentDetailSerializer,
    DocumentCreateSerializer,
    DocumentCheckoutSerializer,
    DocumentChangeOrderSerializer,
    DocumentSnapshotSerializer,
    DocumentVersionSerializer,
    DocumentApproverSerializer,
    CheckoutActionSerializer,
    CheckinActionSerializer,
    LifecycleTransitionSerializer,
)


class DocumentInfocardTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for document infocard types.
    """
    queryset = DocumentInfocardType.objects.all()
    serializer_class = DocumentInfocardTypeSerializer
    permission_classes = [IsAuthenticated]


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing documents with full CRUD operations,
    lifecycle management, checkout/checkin, and audit trails.
    """
    queryset = Document.objects.select_related(
        'infocard_type',
        'department',
        'owner',
        'vault_state'
    ).prefetch_related(
        'checkouts',
        'snapshots',
        'versions',
        'approvers',
        'change_orders'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['vault_state', 'lifecycle_stage', 'infocard_type', 'department', 'owner']
    search_fields = ['document_id', 'title', 'description']
    ordering_fields = ['created_at', 'document_id', 'title']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return DocumentListSerializer
        elif self.action == 'retrieve':
            return DocumentDetailSerializer
        elif self.action == 'create':
            return DocumentCreateSerializer
        return DocumentDetailSerializer

    def perform_create(self, serializer):
        """Set owner to current user on creation."""
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        """Update document."""
        serializer.save()

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        """
        Create a checkout record for a document.
        POST body: { "reason": "string" }
        """
        document = self.get_object()
        serializer = CheckoutActionSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                checkout = DocumentCheckout.objects.create(
                    document=document,
                    checked_out_by=request.user,
                    reason=serializer.validated_data.get('reason', '')
                )
                return Response(
                    DocumentCheckoutSerializer(checkout).data,
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def checkin(self, request, pk=None):
        """
        Release checkout and create new version.
        POST body: { "changes_made": "string" }
        """
        document = self.get_object()
        serializer = CheckinActionSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # Release latest checkout
                checkout = document.checkouts.filter(checked_in_at__isnull=True).first()
                if not checkout:
                    return Response(
                        {'error': 'No active checkout found'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Create new version
                version = DocumentVersion.objects.create(
                    document=document,
                    version_number=document.current_version + 1,
                    changes_made=serializer.validated_data.get('changes_made', ''),
                    created_by=request.user
                )
                
                # Update document version
                document.current_version += 1
                document.save()
                
                return Response(
                    DocumentVersionSerializer(version).data,
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def lifecycle_transition(self, request, pk=None):
        """
        Transition document to new lifecycle stage.
        POST body: { "new_stage": "string" }
        """
        document = self.get_object()
        serializer = LifecycleTransitionSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                document.lifecycle_stage = serializer.validated_data['new_stage']
                document.save()
                return Response(
                    DocumentDetailSerializer(document).data,
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve document with e-signature.
        POST body: { "signature": "string", "comment": "string" }
        """
        document = self.get_object()
        
        try:
            signature = request.data.get('signature')
            if not signature:
                return Response(
                    {'error': 'Signature required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create or update approver record
            approver, created = DocumentApprover.objects.update_or_create(
                document=document,
                approved_by=request.user,
                defaults={
                    'signature': signature,
                    'comment': request.data.get('comment', '')
                }
            )
            
            return Response(
                DocumentApproverSerializer(approver).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        """Lock document from editing."""
        document = self.get_object()
        try:
            document.is_locked = True
            document.save()
            return Response(
                DocumentDetailSerializer(document).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def unlock(self, request, pk=None):
        """Unlock document for editing."""
        document = self.get_object()
        try:
            document.is_locked = False
            document.save()
            return Response(
                DocumentDetailSerializer(document).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def snapshots(self, request, pk=None):
        """List all snapshots for a document."""
        document = self.get_object()
        snapshots = document.snapshots.all()
        serializer = DocumentSnapshotSerializer(snapshots, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def approvers(self, request, pk=None):
        """List all approvers for a document."""
        document = self.get_object()
        approvers = document.approvers.all()
        serializer = DocumentApproverSerializer(approvers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """List all versions for a document."""
        document = self.get_object()
        versions = document.versions.all().order_by('-version_number')
        serializer = DocumentVersionSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def audit_trail(self, request, pk=None):
        """Return audit log entries for this document."""
        document = self.get_object()
        # Assuming AuditLog model tracks changes
        # This would need to be implemented based on your audit system
        return Response({
            'document_id': document.id,
            'created_at': document.created_at,
            'created_by': document.created_by.username if document.created_by else None,
            'updated_at': document.updated_at,
            'updated_by': document.updated_by.username if document.updated_by else None,
        })


class DocumentChangeOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing document change orders.
    """
    queryset = DocumentChangeOrder.objects.select_related(
        'document',
        'created_by'
    ).prefetch_related(
        'approvals'
    ).all()
    serializer_class = DocumentChangeOrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['document__document_id', 'description']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """Set created_by to current user."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve a change order.
        POST body: { "signature": "string", "comment": "string" }
        """
        change_order = self.get_object()
        
        try:
            signature = request.data.get('signature')
            if not signature:
                return Response(
                    {'error': 'Signature required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create approval record
            from .models import DocumentChangeApproval
            approval = DocumentChangeApproval.objects.create(
                change_order=change_order,
                approved_by=request.user,
                signature=signature,
                comment=request.data.get('comment', '')
            )
            
            # Update change order status
            change_order.status = 'approved'
            change_order.save()
            
            from .serializers import DocumentChangeApprovalSerializer
            return Response(
                DocumentChangeApprovalSerializer(approval).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
