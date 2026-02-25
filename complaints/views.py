from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count
from django.utils import timezone
from .models import Complaint, MIRRecord, ComplaintAttachment, ComplaintComment
from .serializers import (
    ComplaintListSerializer, ComplaintDetailSerializer,
    ComplaintCreateSerializer,
    MIRRecordSerializer,
    ComplaintAttachmentSerializer, ComplaintCommentSerializer,
    ReportabilityDeterminationSerializer, MDRSubmissionSerializer
)


class ComplaintViewSet(viewsets.ModelViewSet):
    """ViewSet for complaints with list/detail serializer pattern"""
    queryset = Complaint.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'status', 'severity', 'priority', 'event_type',
        'is_reportable_to_fda', 'mdr_submission_status'
    ]
    search_fields = ['complaint_id', 'title', 'description']
    ordering_fields = ['created_at', 'severity', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return ComplaintCreateSerializer
        elif self.action == 'retrieve':
            return ComplaintDetailSerializer
        return ComplaintListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def determine_reportability(self, request, pk=None):
        """Determine if complaint is reportable to FDA"""
        complaint = self.get_object()
        serializer = ReportabilityDeterminationSerializer(data=request.data)

        if serializer.is_valid():
            try:
                complaint.is_reportable_to_fda = serializer.validated_data.get('is_reportable')
                complaint.reportability_justification = serializer.validated_data.get('justification', '')
                complaint.reportability_determined_by = request.user
                complaint.reportability_determined_date = timezone.now().date()
                complaint.updated_by = request.user
                complaint.save()

                # Add comment about reportability determination
                if serializer.validated_data.get('justification'):
                    ComplaintComment.objects.create(
                        complaint=complaint,
                        author=request.user,
                        text=f"Reportability determined: {serializer.validated_data.get('justification')}"
                    )

                return Response(
                    ComplaintDetailSerializer(complaint).data,
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def submit_mdr(self, request, pk=None):
        """Submit MDR (Medical Device Report) for complaint"""
        complaint = self.get_object()
        serializer = MDRSubmissionSerializer(data=request.data)

        if serializer.is_valid():
            try:
                complaint.mdr_submission_status = 'submitted'
                complaint.mdr_submission_date = timezone.now().date()
                complaint.mdr_submission_number = serializer.validated_data.get('mdr_number', '')
                complaint.updated_by = request.user
                complaint.save()

                # Add comment about MDR submission
                ComplaintComment.objects.create(
                    complaint=complaint,
                    author=request.user,
                    text=f"MDR submitted: {serializer.validated_data.get('mdr_number', '')}"
                )

                return Response(
                    {'success': True, 'mdr_submission_status': complaint.mdr_submission_status},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def attachments(self, request, pk=None):
        """Get or upload attachments for a complaint"""
        complaint = self.get_object()

        if request.method == 'GET':
            attachments = ComplaintAttachment.objects.filter(complaint=complaint)
            serializer = ComplaintAttachmentSerializer(attachments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'POST':
            serializer = ComplaintAttachmentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    complaint=complaint,
                    uploaded_by=request.user
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def mir_records(self, request, pk=None):
        """Get or create MIR (Medical Information Request) records for a complaint"""
        complaint = self.get_object()

        if request.method == 'GET':
            mir_records = MIRRecord.objects.filter(complaint=complaint).order_by('-created_at')
            serializer = MIRRecordSerializer(mir_records, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'POST':
            serializer = MIRRecordSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    complaint=complaint,
                    created_by=request.user,
                    updated_by=request.user
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """Get or add comments to a complaint"""
        complaint = self.get_object()

        if request.method == 'GET':
            comments = ComplaintComment.objects.filter(complaint=complaint).order_by('-created_at')
            serializer = ComplaintCommentSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'POST':
            serializer = ComplaintCommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    complaint=complaint,
                    author=request.user
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def audit_trail(self, request, pk=None):
        """Get audit trail for a complaint"""
        complaint = self.get_object()

        audit_data = {
            'complaint_id': complaint.id,
            'complaint_number': complaint.complaint_id,
            'created_by': complaint.created_by.username if complaint.created_by else None,
            'created_at': complaint.created_at,
            'updated_by': complaint.updated_by.username if complaint.updated_by else None,
            'updated_at': complaint.updated_at,
            'current_status': complaint.status,
            'severity': complaint.severity,
            'is_reportable_to_fda': complaint.is_reportable_to_fda,
        }

        return Response(audit_data, status=status.HTTP_200_OK)


class MIRRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for Medical Information Request records"""
    queryset = MIRRecord.objects.all()
    serializer_class = MIRRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['complaint', 'status']
    ordering_fields = ['created_at', 'due_date']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class MDRDashboardViewSet(viewsets.ViewSet):
    """ViewSet for MDR (Medical Device Report) dashboard"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Get MDR dashboard statistics"""
        pending_mdr = Complaint.objects.filter(
            mdr_submission_status__in=['pending', 'in_progress']
        ).count()

        submitted_mdr = Complaint.objects.filter(
            mdr_submission_status='submitted'
        ).count()

        overdue_determinations = Complaint.objects.filter(
            is_reportable_to_fda__isnull=True,
            created_at__lt=timezone.now().date() - timezone.timedelta(days=15)
        ).count()

        data = {
            'pending_mdr_submissions': pending_mdr,
            'submitted_mdr_submissions': submitted_mdr,
            'overdue_reportability_determinations': overdue_determinations,
        }

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def pending_submissions(self, request):
        """Get pending MDR submissions"""
        pending_complaints = Complaint.objects.filter(
            mdr_submission_status__in=['pending', 'in_progress']
        ).order_by('-created_at')

        serializer = ComplaintListSerializer(pending_complaints, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def overdue_determinations(self, request):
        """Get complaints with overdue reportability determinations"""
        overdue_complaints = Complaint.objects.filter(
            is_reportable_to_fda__isnull=True,
            created_at__lt=timezone.now().date() - timezone.timedelta(days=15)
        ).order_by('created_at')

        serializer = ComplaintListSerializer(overdue_complaints, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
