from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import FilterSet, CharFilter, DateFromToRangeFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Complaint, MIRRecord, ComplaintAttachment, ComplaintComment
from .serializers import (
    ComplaintListSerializer, ComplaintDetailSerializer,
    ComplaintCreateSerializer,
    MIRRecordSerializer,
    ComplaintAttachmentSerializer, ComplaintCommentSerializer,
    ReportabilityDeterminationSerializer, MDRSubmissionSerializer
)


class ComplaintFilterSet(FilterSet):
    """FilterSet for Complaint model with comprehensive filtering"""
    search = CharFilter(
        method='filter_search',
        label='Search complaints by ID, title, or description'
    )
    created_at_range = DateFromToRangeFilter(field_name='received_date')

    class Meta:
        model = Complaint
        fields = [
            'status', 'severity', 'priority', 'category', 'complainant_type',
            'is_reportable_to_fda', 'mdr_submission_status', 'event_type'
        ]

    def filter_search(self, queryset, name, value):
        """Search across complaint_id, title, and description"""
        return queryset.filter(
            Q(complaint_id__icontains=value) |
            Q(title__icontains=value) |
            Q(description__icontains=value)
        )


class ComplaintViewSet(viewsets.ModelViewSet):
    """ViewSet for complaints with list/detail serializer pattern"""
    queryset = Complaint.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ComplaintFilterSet
    search_fields = ['complaint_id', 'title', 'description']
    ordering_fields = ['created_at', 'severity', 'status', 'received_date']
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
                complaint.reportability_determination_date = timezone.now().date()
                complaint.updated_by = request.user
                complaint.save()

                # Add comment about reportability determination
                if serializer.validated_data.get('justification'):
                    ComplaintComment.objects.create(
                        complaint=complaint,
                        author=request.user,
                        comment=f"Reportability determined: {serializer.validated_data.get('justification')}"
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
                complaint.mdr_report_number = serializer.validated_data.get('mdr_number', '')
                complaint.updated_by = request.user
                complaint.save()

                # Add comment about MDR submission
                ComplaintComment.objects.create(
                    complaint=complaint,
                    author=request.user,
                    comment=f"MDR submitted: {serializer.validated_data.get('mdr_number', '')}"
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

    @action(detail=False, methods=['get'])
    def complaint_stats(self, request):
        """Get complaint statistics across status, severity, categories, reportable %"""
        queryset = self.get_queryset()

        # Calculate average resolution days
        closed_complaints = queryset.filter(actual_closure_date__isnull=False)
        avg_resolution_days = 0
        if closed_complaints.exists():
            total_days = sum(
                (c.actual_closure_date - c.received_date.date()).days
                for c in closed_complaints
            )
            avg_resolution_days = round(total_days / closed_complaints.count(), 1)

        reportable_count = queryset.filter(is_reportable_to_fda=True).count()
        total = queryset.count()

        stats = {
            'total': total,
            'by_status': dict(
                queryset.values('status').annotate(count=Count('id')).values_list('status', 'count')
            ),
            'by_severity': dict(
                queryset.values('severity').annotate(count=Count('id')).values_list('severity', 'count')
            ),
            'by_category': dict(
                queryset.values('category').annotate(count=Count('id')).values_list('category', 'count')
            ),
            'reportable_percentage': round((reportable_count / total * 100), 1) if total > 0 else 0,
            'reportable_count': reportable_count,
            'avg_resolution_days': avg_resolution_days,
        }

        return Response(stats, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def reportable(self, request):
        """List only reportable complaints (FDA MDR)"""
        reportable_complaints = self.get_queryset().filter(is_reportable_to_fda=True).order_by('-received_date')
        serializer = ComplaintListSerializer(reportable_complaints, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def mdr_dashboard(self, request):
        """MDR-specific statistics and pending submissions"""
        queryset = self.get_queryset()

        pending_submissions = queryset.filter(
            is_reportable_to_fda=True,
            mdr_submission_status__in=['pending', 'in_progress']
        ).count()

        submitted = queryset.filter(
            mdr_submission_status='submitted'
        ).count()

        by_event_type = dict(
            queryset.filter(is_reportable_to_fda=True)
            .values('event_type')
            .annotate(count=Count('id'))
            .values_list('event_type', 'count')
        )

        # Overdue determinations (15 days from received)
        overdue_determinations = queryset.filter(
            is_reportable_to_fda__isnull=True,
            received_date__lt=timezone.now() - timedelta(days=15)
        ).count()

        mdr_data = {
            'pending_mdr_submissions': pending_submissions,
            'submitted_mdr_submissions': submitted,
            'overdue_reportability_determinations': overdue_determinations,
            'by_event_type': by_event_type,
        }

        return Response(mdr_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def create_linked_capa(self, request, pk=None):
        """Create a CAPA from a complaint"""
        complaint = self.get_object()

        if complaint.capa:
            return Response(
                {'error': 'Complaint already has a linked CAPA'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from capa.models import CAPA
            capa = CAPA.objects.create(
                title=f"CAPA for {complaint.complaint_id}: {complaint.title}",
                description=f"Auto-created from complaint {complaint.complaint_id}",
                initiated_from_complaint=complaint,
                status='planning',
                created_by=request.user,
                updated_by=request.user
            )
            complaint.capa = capa
            complaint.save()

            return Response(
                {'success': True, 'capa_id': capa.id},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        """Get activity timeline including status changes and comments"""
        complaint = self.get_object()

        events = []

        # Add comments
        comments = ComplaintComment.objects.filter(complaint=complaint, parent__isnull=True).order_by('created_at')
        for comment in comments:
            events.append({
                'type': 'comment',
                'timestamp': comment.created_at,
                'author': comment.author.get_full_name(),
                'content': comment.comment,
            })

        # Add reportability determination if exists
        if complaint.reportability_determination_date:
            events.append({
                'type': 'reportability_determination',
                'timestamp': complaint.reportability_determination_date,
                'is_reportable': complaint.is_reportable_to_fda,
                'justification': complaint.reportability_justification,
            })

        # Add MDR submission if exists
        if complaint.mdr_submission_date:
            events.append({
                'type': 'mdr_submission',
                'timestamp': complaint.mdr_submission_date,
                'mdr_number': complaint.mdr_report_number,
                'status': complaint.mdr_submission_status,
            })

        # Sort by timestamp
        events.sort(key=lambda x: x['timestamp'], reverse=True)

        return Response(events, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close a complaint with resolution summary"""
        complaint = self.get_object()

        try:
            resolution_summary = request.data.get('resolution_summary', '')

            complaint.status = 'closed'
            complaint.actual_closure_date = timezone.now().date()
            complaint.closed_by = request.user
            complaint.resolution_description = resolution_summary
            complaint.save()

            # Add comment
            if resolution_summary:
                ComplaintComment.objects.create(
                    complaint=complaint,
                    author=request.user,
                    comment=f"Complaint closed: {resolution_summary}"
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


class MIRRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for Medical Information Request records"""
    queryset = MIRRecord.objects.all()
    serializer_class = MIRRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['complaint', 'report_type']
    ordering_fields = ['created_at', 'submitted_date']
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
