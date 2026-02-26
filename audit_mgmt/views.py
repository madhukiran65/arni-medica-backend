from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, DateFromToRangeFilter
from rest_framework.filters import SearchFilter
from django.db.models import Count

from .models import AuditPlan, AuditFinding
from .serializers import (
    AuditPlanSerializer, AuditFindingSerializer, AuditCloseSerializer
)


class AuditPlanFilterSet(FilterSet):
    """FilterSet for AuditPlan with advanced filtering."""
    planned_start_range = DateFromToRangeFilter(
        field_name='planned_start_date',
        label='Planned Start Date Range'
    )

    class Meta:
        model = AuditPlan
        fields = ['audit_type', 'status', 'lead_auditor', 'supplier']


class AuditPlanViewSet(viewsets.ModelViewSet):
    queryset = AuditPlan.objects.all()
    serializer_class = AuditPlanSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = AuditPlanFilterSet
    search_fields = ['audit_id', 'scope', 'supplier']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=False, methods=['get'])
    def audit_stats(self, request):
        """
        Get audit statistics: counts by status, type, and findings breakdown.
        """
        total = self.queryset.count()
        by_status = self.queryset.values('status').annotate(count=Count('id'))
        by_type = self.queryset.values('audit_type').annotate(count=Count('id'))

        total_major_nc = self.queryset.aggregate(total=Count('id', filter=None))['total'] or 0
        major_nc_sum = sum(audit.major_nc for audit in self.queryset)
        minor_nc_sum = sum(audit.minor_nc for audit in self.queryset)
        obs_sum = sum(audit.observations for audit in self.queryset)

        return Response({
            'total_audits': total,
            'by_status': list(by_status),
            'by_type': list(by_type),
            'total_major_nc': major_nc_sum,
            'total_minor_nc': minor_nc_sum,
            'total_observations': obs_sum,
            'total_findings': major_nc_sum + minor_nc_sum + obs_sum,
        })

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """
        Transition audit to in_progress status.
        """
        from django.utils import timezone
        audit_plan = self.get_object()

        audit_plan.status = 'in_progress'
        audit_plan.actual_start_date = timezone.now().date()
        audit_plan.updated_by = request.user
        audit_plan.save()

        return Response(
            AuditPlanSerializer(audit_plan).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Transition audit to completed status with findings summary.
        """
        from django.utils import timezone
        audit_plan = self.get_object()

        audit_plan.status = 'completed'
        audit_plan.actual_end_date = timezone.now().date()

        # Update findings counts
        audit_plan.update_findings_count()

        audit_plan.updated_by = request.user
        audit_plan.save()

        return Response(
            AuditPlanSerializer(audit_plan).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def add_finding(self, request, pk=None):
        """
        Create a finding linked to this audit.
        """
        audit_plan = self.get_object()

        finding_data = request.data.copy()
        finding_data['audit'] = audit_plan.id

        serializer = AuditFindingSerializer(data=finding_data)
        if serializer.is_valid():
            serializer.save(created_by=request.user, updated_by=request.user)
            audit_plan.update_findings_count()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        """
        Get activity timeline for an audit.
        """
        audit_plan = self.get_object()

        timeline_data = {
            'created': {
                'date': audit_plan.created_at,
                'action': 'Audit Plan Created',
                'user': audit_plan.created_by.username if audit_plan.created_by else 'System'
            },
            'started': None,
            'completed': None,
            'findings': []
        }

        if audit_plan.actual_start_date:
            timeline_data['started'] = {
                'date': audit_plan.actual_start_date,
                'action': 'Audit Started'
            }

        if audit_plan.actual_end_date:
            timeline_data['completed'] = {
                'date': audit_plan.actual_end_date,
                'action': 'Audit Completed',
                'findings_summary': {
                    'major_nc': audit_plan.major_nc,
                    'minor_nc': audit_plan.minor_nc,
                    'observations': audit_plan.observations
                }
            }

        for finding in audit_plan.findings.all():
            timeline_data['findings'].append({
                'date': finding.created_at,
                'action': f'{finding.get_category_display()} - {finding.finding_id}',
                'status': finding.status
            })

        return Response(timeline_data)

    @action(detail=True, methods=['get'])
    def findings(self, request, pk=None):
        """Get all findings for an audit plan"""
        audit_plan = self.get_object()
        findings = audit_plan.findings.all()
        serializer = AuditFindingSerializer(findings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close audit plan"""
        audit_plan = self.get_object()
        serializer = AuditCloseSerializer(data=request.data)

        if serializer.is_valid():
            audit_plan.status = 'closed'
            audit_plan.actual_end_date = serializer.validated_data['actual_end_date']
            if 'next_audit_planned' in serializer.validated_data:
                audit_plan.next_audit_planned = serializer.validated_data['next_audit_planned']
            audit_plan.updated_by = request.user
            audit_plan.save()

            return Response(
                AuditPlanSerializer(audit_plan).data,
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuditFindingViewSet(viewsets.ModelViewSet):
    queryset = AuditFinding.objects.all()
    serializer_class = AuditFindingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['audit', 'category', 'status']
    search_fields = ['finding_id', 'description', 'evidence']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
        # Update parent audit's findings count
        if serializer.instance.audit:
            serializer.instance.audit.update_findings_count()

    @action(detail=True, methods=['post'])
    def link_capa(self, request, pk=None):
        """
        Link finding to existing or new CAPA.
        """
        finding = self.get_object()
        capa_id = request.data.get('capa_id')

        if capa_id:
            finding.assigned_capa_id = capa_id
            finding.status = 'capa_assigned'
            finding.updated_by = request.user
            finding.save()

            return Response(
                AuditFindingSerializer(finding).data,
                status=status.HTTP_200_OK
            )

        return Response(
            {'error': 'capa_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Mark finding as resolved.
        """
        finding = self.get_object()
        finding.status = 'resolved'
        finding.updated_by = request.user
        finding.save()

        return Response(
            AuditFindingSerializer(finding).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """
        Close finding after CAPA completion.
        """
        from django.utils import timezone
        finding = self.get_object()

        finding.status = 'closed'
        finding.actual_closure_date = timezone.now().date()
        finding.updated_by = request.user
        finding.save()

        # Update parent audit's findings count
        if finding.audit:
            finding.audit.update_findings_count()

        return Response(
            AuditFindingSerializer(finding).data,
            status=status.HTTP_200_OK
        )
