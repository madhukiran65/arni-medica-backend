from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count, F
from django.utils import timezone
from .models import (
    JobFunction, TrainingCourse, TrainingPlan, TrainingAssignment,
    TrainingAssessment
)
from .serializers import (
    JobFunctionSerializer,
    TrainingCourseListSerializer, TrainingCourseDetailSerializer,
    TrainingPlanSerializer,
    TrainingAssignmentListSerializer, TrainingAssignmentDetailSerializer,
    TrainingAssessmentSerializer,
    SubmitAssessmentSerializer, AssignTrainingSerializer
)


class JobFunctionViewSet(viewsets.ModelViewSet):
    """ViewSet for CRUD operations on job functions"""
    queryset = JobFunction.objects.all()
    serializer_class = JobFunctionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class TrainingCourseViewSet(viewsets.ModelViewSet):
    """ViewSet for training courses with list/detail serializer pattern"""
    queryset = TrainingCourse.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['course_type', 'status', 'department', 'has_assessment']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TrainingCourseDetailSerializer
        return TrainingCourseListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['get'])
    def assessment(self, request, pk=None):
        """Get assessment for a training course"""
        course = self.get_object()
        try:
            assessment = TrainingAssessment.objects.get(course=course)
            serializer = TrainingAssessmentSerializer(assessment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except TrainingAssessment.DoesNotExist:
            return Response(
                {'detail': 'No assessment found for this course'},
                status=status.HTTP_404_NOT_FOUND
            )


class TrainingPlanViewSet(viewsets.ModelViewSet):
    """ViewSet for CRUD operations on training plans"""
    queryset = TrainingPlan.objects.all()
    serializer_class = TrainingPlanSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['job_function', 'is_active', 'is_mandatory']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class TrainingAssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for training assignments with custom actions"""
    queryset = TrainingAssignment.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'user', 'course']
    search_fields = ['user__username', 'course__title']
    ordering_fields = ['assigned_date', 'due_date', 'status']
    ordering = ['-assigned_date']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TrainingAssignmentDetailSerializer
        elif self.action in ['submit_assessment', 'complete']:
            return SubmitAssessmentSerializer
        return TrainingAssignmentListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=False, methods=['get'])
    def my_assignments(self, request):
        """Get current user's training assignments"""
        assignments = self.queryset.filter(user=request.user)
        serializer = self.get_serializer(assignments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def submit_assessment(self, request, pk=None):
        """Submit assessment responses for a training assignment"""
        assignment = self.get_object()
        serializer = SubmitAssessmentSerializer(data=request.data)

        if serializer.is_valid():
            try:
                # Process assessment submission
                responses = serializer.validated_data.get('responses', [])
                # Logic to save assessment responses would go here
                assignment.status = 'assessment_submitted'
                assignment.updated_by = request.user
                assignment.save()

                return Response(
                    {'success': True, 'message': 'Assessment submitted successfully'},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark training assignment as complete"""
        assignment = self.get_object()
        serializer = SubmitAssessmentSerializer(data=request.data)

        if serializer.is_valid():
            assignment.status = 'completed'
            assignment.completion_date = timezone.now().date()
            assignment.passed = serializer.validated_data.get('passed', True)
            assignment.score = serializer.validated_data.get('score')
            assignment.updated_by = request.user
            assignment.save()

            return Response(
                TrainingAssignmentDetailSerializer(assignment).data,
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TrainingAssessmentViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only ViewSet for training assessments"""
    queryset = TrainingAssessment.objects.all()
    serializer_class = TrainingAssessmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['course']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class ComplianceDashboardViewSet(viewsets.ViewSet):
    """ViewSet for compliance dashboard statistics"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Get overall compliance statistics"""
        today = timezone.now().date()

        total_assignments = TrainingAssignment.objects.count()
        completed_assignments = TrainingAssignment.objects.filter(status='completed').count()
        overdue_assignments = TrainingAssignment.objects.filter(
            Q(status__in=['assigned', 'in_progress']) & Q(due_date__lt=today)
        ).count()
        failed_assignments = TrainingAssignment.objects.filter(status='failed').count()
        in_progress = TrainingAssignment.objects.filter(status='in_progress').count()

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
            'in_progress_assignments': in_progress,
            'overdue_assignments': overdue_assignments,
            'failed_assignments': failed_assignments,
            'compliance_percentage': round(compliance_percentage, 2),
            'mandatory_compliance_percentage': round(mandatory_compliance_percentage, 2),
        }

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue training assignments"""
        today = timezone.now().date()
        overdue_assignments = TrainingAssignment.objects.filter(
            Q(status__in=['assigned', 'in_progress']) & Q(due_date__lt=today)
        ).order_by('due_date')

        serializer = TrainingAssignmentListSerializer(overdue_assignments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get compliance statistics by department"""
        departments = TrainingAssignment.objects.values('user__department').annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            overdue=Count('id', filter=Q(
                Q(status__in=['assigned', 'in_progress']) & 
                Q(due_date__lt=timezone.now().date())
            ))
        ).order_by('user__department')

        data = []
        for dept in departments:
            total = dept['total']
            completed = dept['completed']
            compliance_pct = (completed / total * 100) if total > 0 else 0
            data.append({
                'department': dept['user__department'],
                'total': total,
                'completed': completed,
                'overdue': dept['overdue'],
                'compliance_percentage': round(compliance_pct, 2)
            })

        return Response(data, status=status.HTTP_200_OK)


class AutoAssignView(APIView):
    """APIView for auto-assigning training based on job function"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Auto-assign training courses based on job function"""
        serializer = AssignTrainingSerializer(data=request.data)

        if serializer.is_valid():
            try:
                job_function_id = serializer.validated_data.get('job_function_id')
                department = serializer.validated_data.get('department')

                # Get job function
                try:
                    job_function = JobFunction.objects.get(id=job_function_id)
                except JobFunction.DoesNotExist:
                    return Response(
                        {'error': 'Job function not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )

                # Get required courses for job function
                courses = TrainingCourse.objects.filter(
                    is_mandatory=True,
                    job_functions=job_function
                )

                # Auto-assign courses to users in department with this job function
                from django.contrib.auth import get_user_model
                User = get_user_model()

                assigned_count = 0
                for course in courses:
                    users = User.objects.filter(
                        department=department,
                        job_function=job_function
                    ).exclude(
                        training_assignments__course=course
                    )

                    for user in users:
                        TrainingAssignment.objects.create(
                            user=user,
                            course=course,
                            assigned_by=request.user,
                            due_date=timezone.now().date() + timezone.timedelta(days=30),
                            created_by=request.user,
                            updated_by=request.user
                        )
                        assigned_count += 1

                return Response(
                    {'success': True, 'assignments_created': assigned_count},
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
