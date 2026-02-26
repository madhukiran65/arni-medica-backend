from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters import FilterSet, CharFilter, DateFromToRangeFilter, BooleanFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
import hashlib

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


# ============================================================================
# FILTER SETS
# ============================================================================

class DocumentFilterSet(FilterSet):
    """Enhanced FilterSet for Document with comprehensive filtering options."""

    vault_state = CharFilter(field_name='vault_state', lookup_expr='iexact')
    lifecycle_stage = CharFilter(field_name='lifecycle_stage', lookup_expr='icontains')
    department = CharFilter(field_name='department__name', lookup_expr='icontains')
    infocard_type = CharFilter(field_name='infocard_type__name', lookup_expr='icontains')
    owner = CharFilter(field_name='owner__username', lookup_expr='iexact')
    created_at__gte = DateFromToRangeFilter(field_name='created_at')
    created_at__lte = DateFromToRangeFilter(field_name='created_at')
    requires_training = BooleanFilter(field_name='requires_training')
    is_locked = BooleanFilter(field_name='is_locked')
    requires_approval = BooleanFilter(field_name='requires_approval')

    class Meta:
        model = Document
        fields = [
            'vault_state',
            'lifecycle_stage',
            'department',
            'infocard_type',
            'owner',
            'requires_training',
            'is_locked',
            'requires_approval',
            'created_at__gte',
            'created_at__lte',
        ]


class DocumentInfocardTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for document infocard types.
    """
    queryset = DocumentInfocardType.objects.all()
    serializer_class = DocumentInfocardTypeSerializer
    permission_classes = [IsAuthenticated]


class DocumentViewSet(viewsets.ModelViewSet):
    """
    Enhanced ViewSet for managing documents with full CRUD operations,
    lifecycle management, checkout/checkin, approvals, and audit trails.

    Features:
    - Auto-generated document IDs based on infocard_type prefix
    - Comprehensive filtering and search
    - Bulk release for admin users
    - Pending review tracking
    - User checkout history
    - Document statistics for dashboards
    - File upload with SHA-256 hashing
    - Version auto-increment on checkin
    """
    queryset = Document.objects.select_related(
        'infocard_type',
        'department',
        'owner',
        'locked_by'
    ).prefetch_related(
        'active_checkout',
        'snapshots',
        'versions',
        'approvers',
        'change_orders'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DocumentFilterSet
    search_fields = ['document_id', 'title', 'description', 'subject_keywords']
    ordering_fields = ['created_at', 'document_id', 'title', 'next_review_date', 'vault_state']
    ordering = ['-created_at']
    parser_classes = (MultiPartParser, FormParser)

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return DocumentListSerializer
        elif self.action == 'retrieve':
            return DocumentDetailSerializer
        elif self.action == 'create':
            return DocumentCreateSerializer
        return DocumentDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve with error debugging."""
        import traceback
        try:
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {'error': str(e), 'traceback': traceback.format_exc()},
                status=500
            )

    def perform_create(self, serializer):
        """Set owner to current user on creation."""
        serializer.save(owner=self.request.user, created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        """Override create with clean error handling."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        document = serializer.instance
        return Response(
            DocumentDetailSerializer(document).data,
            status=status.HTTP_201_CREATED
        )

    def perform_update(self, serializer):
        """Update document and set updated_by."""
        serializer.save(updated_by=self.request.user)

    # ========================================================================
    # DOCUMENT LIFECYCLE ACTIONS
    # ========================================================================

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        """
        Check out a document for editing.

        POST body: {
            "checkout_reason": "string (required)",
            "expected_checkin_date": "ISO datetime (optional)"
        }
        """
        document = self.get_object()

        # Validation: check if already checked out
        if document.active_checkout and document.active_checkout.is_active:
            return Response(
                {
                    'error': 'Document is already checked out',
                    'checked_out_by': document.active_checkout.checked_out_by.username,
                    'checked_out_at': document.active_checkout.checked_out_at.isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validation: only draft documents can be checked out
        if document.vault_state != 'draft':
            return Response(
                {'error': f'Only draft documents can be checked out. Current state: {document.vault_state}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CheckoutActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Invalidate any previous active checkouts
            DocumentCheckout.objects.filter(
                document=document,
                is_active=True
            ).update(is_active=False)

            checkout = DocumentCheckout.objects.create(
                document=document,
                checked_out_by=request.user,
                checkout_reason=serializer.validated_data.get('checkout_reason', ''),
                expected_checkin_date=serializer.validated_data.get('expected_checkin_date')
            )

            return Response(
                DocumentCheckoutSerializer(checkout).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': f'Checkout failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def checkin(self, request, pk=None):
        """
        Check in a document and auto-increment minor version.

        POST body: {
            "file": "file (optional)",
            "change_summary": "string (required)",
            "is_major_change": "boolean (default: false)"
        }
        """
        document = self.get_object()
        serializer = CheckinActionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validation: document must be checked out
            checkout = document.active_checkout
            if not checkout or not checkout.is_active:
                return Response(
                    {'error': 'Document is not currently checked out'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validation: only the user who checked out can check in
            if checkout.checked_out_by != request.user:
                return Response(
                    {
                        'error': 'Only the user who checked out this document can check it in',
                        'checked_out_by': checkout.checked_out_by.username
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            # Process file upload if provided
            if 'file' in request.FILES:
                document.file = request.FILES['file']
                document.original_filename = request.FILES['file'].name
                document.file_type = request.FILES['file'].content_type
                document.file_size = request.FILES['file'].size
                document.file_hash = self._calculate_file_hash(request.FILES['file'])

            # Auto-increment minor version
            is_major = serializer.validated_data.get('is_major_change', False)
            if is_major:
                document.major_version += 1
                document.minor_version = 0
            else:
                document.minor_version += 1

            document.change_summary = serializer.validated_data.get('change_summary', '')
            document.updated_by = request.user
            document.save()

            # Create version snapshot
            version = DocumentVersion.objects.create(
                document=document,
                major_version=document.major_version,
                minor_version=document.minor_version,
                change_type='major' if is_major else 'minor',
                is_major_change=is_major,
                change_summary=document.change_summary,
                snapshot_data={
                    'title': document.title,
                    'vault_state': document.vault_state,
                    'version': document.version_string
                },
                released_date=timezone.now()
            )

            # Close checkout
            checkout.is_active = False
            checkout.save()

            return Response(
                DocumentVersionSerializer(version).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': f'Check-in failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def bulk_release(self, request):
        """
        Release multiple documents at once (admin only).

        POST body: {
            "document_ids": [1, 2, 3, ...]
        }
        """
        # Check admin permission
        if not request.user.is_staff:
            return Response(
                {'error': 'Only administrators can perform bulk release'},
                status=status.HTTP_403_FORBIDDEN
            )

        doc_ids = request.data.get('document_ids', [])
        if not doc_ids:
            return Response(
                {'error': 'document_ids list is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            documents = Document.objects.filter(id__in=doc_ids)
            released_count = 0

            for doc in documents:
                if doc.vault_state != 'released':
                    doc.vault_state = 'released'
                    doc.released_date = timezone.now()
                    doc.save()
                    released_count += 1

            return Response(
                {
                    'success': True,
                    'released_count': released_count,
                    'total_requested': len(doc_ids),
                    'message': f'{released_count} document(s) released'
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': f'Bulk release failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def pending_review(self, request):
        """
        List documents past their next_review_date.

        Returns paginated list of documents with overdue reviews.
        """
        today = timezone.now().date()
        overdue = Document.objects.filter(
            next_review_date__lt=today
        ).select_related('owner', 'department').order_by('next_review_date')

        page = self.paginate_queryset(overdue)
        if page is not None:
            serializer = DocumentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = DocumentListSerializer(overdue, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_checkouts(self, request):
        """
        List documents checked out by current user.
        """
        checkouts = DocumentCheckout.objects.filter(
            checked_out_by=request.user,
            is_active=True
        ).select_related('document').order_by('-checked_out_at')

        documents = [co.document for co in checkouts]
        page = self.paginate_queryset(documents)
        if page is not None:
            serializer = DocumentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = DocumentListSerializer(documents, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def document_stats(self, request):
        """
        Return statistics for document dashboard.

        Returns: {
            "total_documents": int,
            "by_vault_state": { "draft": int, "released": int, ... },
            "by_infocard_type": { "SOP": int, "FORM": int, ... },
            "overdue_reviews": int,
            "locked_documents": int,
            "checked_out_documents": int,
            "my_documents": int
        }
        """
        total = Document.objects.count()
        today = timezone.now().date()

        # Group by vault_state
        by_state = Document.objects.values('vault_state').annotate(
            count=Count('id')
        ).order_by('vault_state')

        # Group by infocard_type
        by_type = Document.objects.values('infocard_type__prefix').annotate(
            count=Count('id')
        ).order_by('infocard_type__prefix')

        overdue = Document.objects.filter(
            next_review_date__lt=today
        ).count()

        locked = Document.objects.filter(is_locked=True).count()

        checked_out = DocumentCheckout.objects.filter(
            is_active=True
        ).count()

        my_docs = Document.objects.filter(owner=request.user).count()

        return Response({
            'total_documents': total,
            'by_vault_state': {item['vault_state']: item['count'] for item in by_state},
            'by_infocard_type': {item['infocard_type__prefix']: item['count'] for item in by_type},
            'overdue_reviews': overdue,
            'locked_documents': locked,
            'checked_out_documents': checked_out,
            'my_documents': my_docs,
        })

    @action(detail=True, methods=['post'], parser_classes=(MultiPartParser, FormParser))
    def upload_file(self, request, pk=None):
        """
        Upload and attach a file to a document.

        POST (multipart): {
            "file": "file (required)"
        }

        Returns SHA-256 hash of uploaded file.
        """
        document = self.get_object()

        if 'file' not in request.FILES:
            return Response(
                {'error': 'file is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            uploaded_file = request.FILES['file']

            # Calculate SHA-256 hash
            file_hash = self._calculate_file_hash(uploaded_file)

            # Save file to document
            document.file = uploaded_file
            document.original_filename = uploaded_file.name
            document.file_type = uploaded_file.content_type
            document.file_size = uploaded_file.size
            document.file_hash = file_hash
            document.save()

            return Response({
                'success': True,
                'file_name': uploaded_file.name,
                'file_size': uploaded_file.size,
                'file_type': uploaded_file.content_type,
                'file_hash': file_hash,
                'hash_algorithm': 'SHA-256'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'File upload failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _calculate_file_hash(self, file_obj):
        """Calculate SHA-256 hash of a file object."""
        hasher = hashlib.sha256()
        for chunk in file_obj.chunks():
            hasher.update(chunk)
        return hasher.hexdigest()

    # ========================================================================
    # DOCUMENT STATE TRANSITION ACTIONS
    # ========================================================================

    @action(detail=True, methods=['post'])
    def lifecycle_transition(self, request, pk=None):
        """
        Transition document to new lifecycle stage.

        POST body: {
            "target_stage": "string",
            "comments": "string (optional)"
        }
        """
        document = self.get_object()
        serializer = LifecycleTransitionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            document.lifecycle_stage = serializer.validated_data['target_stage']
            document.updated_by = request.user
            document.save()

            return Response(
                DocumentDetailSerializer(document).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': f'Transition failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve document with e-signature.

        POST body: {
            "signature": "string (required)",
            "comment": "string (optional)"
        }
        """
        document = self.get_object()

        signature = request.data.get('signature')
        if not signature:
            return Response(
                {'error': 'Signature is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            approver, created = DocumentApprover.objects.update_or_create(
                document=document,
                approver=request.user,
                defaults={
                    'approval_status': 'approved',
                    'approved_at': timezone.now(),
                    'comments': request.data.get('comment', '')
                }
            )

            return Response(
                DocumentApproverSerializer(approver).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': f'Approval failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        """Lock document from further edits."""
        document = self.get_object()
        try:
            document.is_locked = True
            document.locked_by = request.user
            document.locked_at = timezone.now()
            document.lock_reason = request.data.get('reason', '')
            document.save()

            return Response(
                DocumentDetailSerializer(document).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': f'Lock failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def unlock(self, request, pk=None):
        """Unlock document for editing."""
        document = self.get_object()

        # Only document owner or staff can unlock
        if document.locked_by != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Only the user who locked this document can unlock it'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            document.is_locked = False
            document.locked_by = None
            document.locked_at = None
            document.lock_reason = ''
            document.save()

            return Response(
                DocumentDetailSerializer(document).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': f'Unlock failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    # ========================================================================
    # DOCUMENT METADATA RETRIEVAL ACTIONS
    # ========================================================================

    @action(detail=True, methods=['get'])
    def snapshots(self, request, pk=None):
        """List all snapshots for a document."""
        document = self.get_object()
        snapshots = document.snapshots.all().order_by('-created_at')
        serializer = DocumentSnapshotSerializer(snapshots, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def approvers(self, request, pk=None):
        """List all approvers for a document with their approval status."""
        document = self.get_object()
        approvers = document.approvers.all().order_by('sequence')
        serializer = DocumentApproverSerializer(approvers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """List all versions for a document."""
        document = self.get_object()
        versions = document.versions.all().order_by('-major_version', '-minor_version')

        page = self.paginate_queryset(versions)
        if page is not None:
            serializer = DocumentVersionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = DocumentVersionSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def audit_trail(self, request, pk=None):
        """Return audit log entries for this document."""
        document = self.get_object()

        # Collect all document changes from audit trail
        checkouts = DocumentCheckout.objects.filter(document=document).order_by('-checked_out_at')
        versions = DocumentVersion.objects.filter(document=document).order_by('-created_at')
        approvals = DocumentApprover.objects.filter(document=document).order_by('-approved_at')

        # Build timeline
        timeline = []

        # Document creation
        timeline.append({
            'timestamp': document.created_at,
            'action': 'created',
            'user': document.created_by.username if document.created_by else 'System',
            'details': f'Document {document.document_id} created'
        })

        # Checkouts
        for checkout in checkouts:
            timeline.append({
                'timestamp': checkout.checked_out_at,
                'action': 'checked_out',
                'user': checkout.checked_out_by.username if checkout.checked_out_by else 'Unknown',
                'details': f'Reason: {checkout.checkout_reason}'
            })

        # Versions
        for version in versions:
            timeline.append({
                'timestamp': version.created_at,
                'action': 'version_created',
                'user': version.created_by.username if version.created_by else 'System',
                'details': f'Version {version.major_version}.{version.minor_version} - {version.change_summary}'
            })

        # Approvals
        for approval in approvals:
            if approval.approved_at:
                timeline.append({
                    'timestamp': approval.approved_at,
                    'action': 'approved',
                    'user': approval.approver.username if approval.approver else 'Unknown',
                    'details': f'Status: {approval.approval_status} - {approval.comments}'
                })

        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'], reverse=True)

        return Response({
            'document_id': document.document_id,
            'audit_trail': timeline,
            'total_events': len(timeline)
        })


class DocumentChangeOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing document change orders with approval workflows.
    """
    queryset = DocumentChangeOrder.objects.select_related(
        'document',
        'proposed_by'
    ).prefetch_related(
        'approvals'
    ).all()
    serializer_class = DocumentChangeOrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['document__document_id', 'change_number', 'description', 'title']
    ordering_fields = ['created_at', 'status', 'change_number']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """Set proposed_by to current user."""
        serializer.save(proposed_by=self.request.user)

    def perform_update(self, serializer):
        """Update change order."""
        serializer.save()

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve a change order.

        POST body: {
            "comment": "string (optional)"
        }
        """
        change_order = self.get_object()

        try:
            from .models import DocumentChangeApproval

            approval, created = DocumentChangeApproval.objects.update_or_create(
                change_order=change_order,
                approver=request.user,
                defaults={
                    'status': 'approved',
                    'approved_at': timezone.now(),
                    'comments': request.data.get('comment', '')
                }
            )

            # Update change order status if all approvals are done
            all_approvals = change_order.approvals.all()
            if all_approvals.filter(status__in=['pending', 'rejected']).count() == 0:
                change_order.status = 'approved'
                change_order.save()

            from .serializers import DocumentChangeApprovalSerializer
            return Response(
                DocumentChangeApprovalSerializer(approval).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': f'Approval failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject a change order.

        POST body: {
            "comment": "string (required)"
        }
        """
        change_order = self.get_object()
        comment = request.data.get('comment', '')

        if not comment:
            return Response(
                {'error': 'comment is required for rejection'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from .models import DocumentChangeApproval

            approval, created = DocumentChangeApproval.objects.update_or_create(
                change_order=change_order,
                approver=request.user,
                defaults={
                    'status': 'rejected',
                    'approved_at': timezone.now(),
                    'comments': comment
                }
            )

            # Update change order status to rejected
            change_order.status = 'rejected'
            change_order.save()

            from .serializers import DocumentChangeApprovalSerializer
            return Response(
                DocumentChangeApprovalSerializer(approval).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': f'Rejection failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
