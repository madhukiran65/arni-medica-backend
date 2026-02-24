from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from django.utils import timezone
from .models import TrainingCourse, TrainingAssignment
from .serializers import (
    TrainingCourseSerializer, TrainingAssignmentSerializer,
    ComplianceDashboardSerializer
)


class TrainingCourseViewSet(viewsets.ModelViewSet):
    queryset = TrainingCourse.objects.all()
    serializer_class = TrainingCourseSerializer
    permission_classes = [IsAuthenticated]


class TrainingAssignmentViewSet(viewsets.ModelViewSet):
    queryset = TrainingAssignment.objects.all()
    serializer_class = TrainingAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=False, methods=['get'])
    def compliance_dashboard(self, request):
        """Get training compliance dashboard"""
        today = timezone.now().date()
        
        total_assignments = TrainingAssignment.objects.count()
        completed_assignments = TrainingAssignment.objects.filter(status='completed').count()
        overdue_assignments = TrainingAssignment.objects.filter(
            Q(status__in=['assigned', 'in_progress']) & Q(due_date__lt=today)
        ).count()
        failed_assignments = TrainingAssignment.objects.filter(status='failed').count()
        
        compliance_percentage = 0
        if total_assignments > 0:
            compliance_percentage = (completed_assignments / total_assignments) * 100

        mandatory_courses = TrainingCourse.objects.filter(is_mandatory=True)
        mandatory_assignments = TrainingAssignment.objects.filter(course__in=mandatory_courses)
        mandatory_completed = mandatory_assignments.filter(status='completed').count()
        
        mandatory_compliance_percentage = 0
        if mandatory_assignments.count() > 0:
            mandatory_compliance_percentage = (mandatory_completed / mandatory_assignments.count()) * 100

        data = {
            'total_assignments': total_assignments,
            'completed_assignments': completed_assignments,
            'overdue_assignments': overdue_assignments,
            'failed_assignments': failed_assignments,
            'compliance_percentage': compliance_percentage,
            'mandatory_compliance_percentage': mandatory_compliance_percentage,
        }
        
        serializer = ComplianceDashboardSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        """Mark training assignment as complete"""
        assignment = self.get_object()
        assignment.status = 'completed'
        assignment.completion_date = timezone.now().date()
        assignment.passed = request.data.get('passed', True)
        assignment.score = request.data.get('score')
        assignment.updated_by = request.user
        assignment.save()
        
        return Response(
            TrainingAssignmentSerializer(assignment).data,
            status=status.HTTP_200_OK
        )
