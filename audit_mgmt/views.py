from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import AuditPlan, AuditFinding
from .serializers import (
    AuditPlanSerializer, AuditFindingSerializer, AuditCloseSerializer
)


class AuditPlanViewSet(viewsets.ModelViewSet):
    queryset = AuditPlan.objects.all()
    serializer_class = AuditPlanSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

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

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
        # Update parent audit's findings count
        if serializer.instance.audit:
            serializer.instance.audit.update_findings_count()
