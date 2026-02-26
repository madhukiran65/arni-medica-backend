from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.db import connection
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import hashlib
from core.models import AuditLog, ElectronicSignature, Notification
from core.serializers import (
    AuditLogSerializer, ElectronicSignatureSerializer,
    SignatureRequestSerializer, InvalidateSignatureSerializer,
    NotificationSerializer
)
from core.permissions import CanViewAuditTrail, CanSignDocuments
from core.pdf_export import generate_capa_report, generate_deviation_report, generate_audit_report


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only audit log (21 CFR Part 11). No create/update/delete via API."""
    queryset = AuditLog.objects.select_related('user', 'content_type').all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, CanViewAuditTrail]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'user', 'content_type']
    search_fields = ['object_repr', 'change_summary']
    ordering_fields = ['timestamp', 'action']


class ElectronicSignatureViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing electronic signatures (21 CFR Part 11).
    Supports:
    - Listing signatures for any object (filtered by content_type and object_id)
    - Creating new signatures (requires password re-authentication)
    - Invalidating signatures (requires password re-authentication)
    """
    queryset = ElectronicSignature.objects.select_related(
        'signer', 'invalidated_by', 'content_type'
    ).all()
    serializer_class = ElectronicSignatureSerializer
    permission_classes = [IsAuthenticated, CanSignDocuments]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['content_type', 'object_id', 'signer', 'is_valid']
    ordering_fields = ['-timestamp', 'signer']

    def get_queryset(self):
        """Filter signatures by content_type and object_id if provided."""
        queryset = super().get_queryset()
        content_type = self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')

        if content_type and object_id:
            queryset = queryset.filter(content_type__id=content_type, object_id=object_id)

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Create a new electronic signature.
        Requires password re-authentication for 21 CFR Part 11 compliance.
        """
        serializer = SignatureRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Verify password (21 CFR Part 11 requirement)
        user = request.user
        password = serializer.validated_data.get('password')
        if not user.check_password(password):
            return Response(
                {'detail': 'Invalid password. Signature requires password verification.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Extract signature details
        signature_meaning = serializer.validated_data.get('signature_meaning')
        reason = serializer.validated_data.get('reason')
        meaning = serializer.validated_data.get('meaning')
        content_hash = serializer.validated_data.get('content_hash')

        # Get content_type and object_id from request
        content_type_id = request.data.get('content_type')
        object_id = request.data.get('object_id')

        if not content_type_id or not object_id:
            return Response(
                {'detail': 'content_type and object_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            content_type = ContentType.objects.get(id=content_type_id)
        except ContentType.DoesNotExist:
            return Response(
                {'detail': 'Invalid content_type'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get client IP address
        ip_address = self._get_client_ip(request)

        # Create signature using static method
        try:
            # Compute signature_hash
            from django.utils import timezone
            timestamp = timezone.now()
            sig_input = f"{user.id}|{content_hash}|{timestamp.isoformat()}"
            signature_hash = hashlib.sha256(sig_input.encode()).hexdigest()

            signature = ElectronicSignature.objects.create(
                content_type=content_type,
                object_id=str(object_id),
                signer=user,
                timestamp=timestamp,
                signature_meaning=signature_meaning,
                reason=reason,
                meaning=meaning,
                content_hash=content_hash,
                signature_hash=signature_hash,
                ip_address=ip_address,
            )

            # Log the signature creation in audit trail
            AuditLog.objects.create(
                content_type=content_type,
                object_id=str(object_id),
                object_repr=f"Signed with {signature_meaning}",
                user=user,
                action='sign',
                timestamp=timestamp,
                ip_address=ip_address,
                change_summary=f"Electronic signature created: {meaning}",
            )

            serializer = self.get_serializer(signature)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'detail': f'Error creating signature: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def invalidate(self, request, pk=None):
        """
        Invalidate an electronic signature.
        Requires password re-authentication and invalidation reason.
        """
        signature = self.get_object()

        if not signature.is_valid:
            return Response(
                {'detail': 'Signature is already invalidated'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = InvalidateSignatureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Verify password
        user = request.user
        password = serializer.validated_data.get('password')
        if not user.check_password(password):
            return Response(
                {'detail': 'Invalid password. Invalidation requires password verification.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        invalidation_reason = serializer.validated_data.get('invalidation_reason')

        # Invalidate the signature
        signature.invalidate(user, invalidation_reason)

        # Log invalidation in audit trail
        AuditLog.objects.create(
            content_type=signature.content_type,
            object_id=str(signature.object_id),
            object_repr=f"Signature invalidated",
            user=user,
            action='update',
            timestamp=signature.invalidated_at,
            ip_address=self._get_client_ip(request),
            change_summary=f"Electronic signature invalidated. Reason: {invalidation_reason}",
        )

        serializer = self.get_serializer(signature)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def _get_client_ip(request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing user notifications.
    Provides listing, filtering, and marking notifications as read.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['notification_type', 'is_read']
    ordering_fields = ['-sent_at', 'notification_type']
    ordering = ['-sent_at']

    def get_queryset(self):
        """Return notifications for the current user only."""
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark a notification as read."""
        notification = self.get_object()
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all unread notifications as read for current user."""
        Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        return Response({'status': 'All notifications marked as read'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        return Response({'unread_count': count})


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for monitoring and load balancers.
    Verifies database connectivity and service status.
    """
    database_status = 'healthy'
    try:
        connection.ensure_connection()
    except Exception as e:
        database_status = 'unhealthy'

    overall_status = 'healthy' if database_status == 'healthy' else 'degraded'

    return Response({
        'status': overall_status,
        'database': database_status,
        'version': '1.0.0',
        'app': 'Arni eQMS',
        'debug': settings.DEBUG,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def setup_initial_data(request):
    """
    One-time setup endpoint to create superuser and seed reference data.
    Protected by setup secret key.
    """
    setup_key = request.data.get('setup_key', '')
    if setup_key != 'arni-medica-setup-2026':
        return Response({'error': 'Invalid setup key'}, status=403)

    from django.contrib.auth.models import User
    from django.core.management import call_command
    import io

    results = {}

    # Create superuser if not exists
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@arnimedica.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        results['superuser'] = 'Created admin user'
    else:
        results['superuser'] = 'Admin user already exists'

    # Create additional test users
    test_users = [
        ('qa_manager', 'qa@arnimedica.com', 'QA', 'Manager'),
        ('doc_controller', 'docs@arnimedica.com', 'Document', 'Controller'),
        ('training_admin', 'training@arnimedica.com', 'Training', 'Admin'),
        ('capa_owner', 'capa@arnimedica.com', 'CAPA', 'Owner'),
    ]
    users_created = 0
    for username, email, first, last in test_users:
        if not User.objects.filter(username=username).exists():
            User.objects.create_user(
                username=username, email=email, password='test123',
                first_name=first, last_name=last
            )
            users_created += 1
    results['test_users'] = f'Created {users_created} test users'

    # Run seed data command
    output = io.StringIO()
    try:
        call_command('seed_data', stdout=output)
        results['seed_data'] = output.getvalue().strip()
    except Exception as e:
        results['seed_data'] = f'Error: {str(e)}'

    return Response(results)


# ============================================================================
# PDF EXPORT ENDPOINTS
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_capa_pdf(request, capa_id):
    """
    Export a CAPA record as a PDF file.
    GET /api/export/capa/<id>/pdf/
    """
    try:
        pdf_buffer = generate_capa_report(capa_id)
        return FileResponse(
            pdf_buffer,
            as_attachment=True,
            filename=f'CAPA-{capa_id}.pdf',
            content_type='application/pdf'
        )
    except ObjectDoesNotExist as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error generating PDF: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_deviation_pdf(request, deviation_id):
    """
    Export a Deviation record as a PDF file.
    GET /api/export/deviation/<id>/pdf/
    """
    try:
        pdf_buffer = generate_deviation_report(deviation_id)
        return FileResponse(
            pdf_buffer,
            as_attachment=True,
            filename=f'Deviation-{deviation_id}.pdf',
            content_type='application/pdf'
        )
    except ObjectDoesNotExist as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error generating PDF: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_audit_pdf(request, audit_id):
    """
    Export an Audit Plan record as a PDF file.
    GET /api/export/audit/<id>/pdf/
    """
    try:
        pdf_buffer = generate_audit_report(audit_id)
        return FileResponse(
            pdf_buffer,
            as_attachment=True,
            filename=f'Audit-{audit_id}.pdf',
            content_type='application/pdf'
        )
    except ObjectDoesNotExist as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error generating PDF: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
