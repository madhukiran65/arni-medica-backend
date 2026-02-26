from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count, F, Avg, Sum, Case, When, DecimalField
from django.utils import timezone
from django.contrib.auth.models import User
from .models import (
    JobFunction, TrainingCourse, TrainingPlan, TrainingAssignment,
    TrainingAssessment, TrainingCompetency, TrainingComplianceRecord
)
from .serializers import (
    JobFunctionSerializer,
    TrainingCourseListSerializer, TrainingCourseDetailSerializer,
    TrainingPlanSerializer,
    TrainingAssignmentListSerializer, TrainingAssignmentDetailSerializer,
    TrainingAssessmentSerializer,
    TrainingCompetencySerializer,
    SubmitAssessmentSerializer, AssignTrainingSerializer,
    TrainingComplianceRecordSerializer
)


class JobFunctionViewSet(viewsets.ModelViewSet):
    """ViewSet for full CRUD operations on job functions"""
    queryset = JobFunction.objects.all()
    serializer_class = JobFunctionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['department', 'is_active', 'parent']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """List all users with this job function"""
        job_function = self.get_object()
        # Get users associated with this job function through their profile
        users = User.objects.filter(
            profile__job_function=job_function
        ).select_related('profile').distinct()

        from .serializers import UserSerializer
        serializer = UserSerializer(users, many=True)
        return Response({
            'job_function_id': job_function.id,
            'job_function_name': job_function.name,
            'count': users.count(),
            'users': serializer.data
        })

    @action(detail=True, methods=['get'])
    def required_courses(self, request, pk=None):
        """List courses required for this job function"""
        job_function = self.get_object()
        courses = TrainingCourse.objects.filter(
            applicable_job_functions=job_function,
            status='active'
        ).prefetch_related('competencies')

        serializer = TrainingCourseListSerializer(courses, many=True)
        return Response({
            'job_function_id': job_function.id,
            'job_function_name': job_function.name,
            'count': courses.count(),
            'courses': serializer.data
        })


class TrainingCompetencyViewSet(viewsets.ModelViewSet):
    """ViewSet for CRUD operations on training competencies"""
    queryset = TrainingCompetency.objects.all()
    serializer_class = TrainingCompetencySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['course', 'is_mandatory', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class TrainingCourseViewSet(viewsets.ModelViewSet):
    """ViewSet for training courses with enhanced filtering and actions"""
    queryset = TrainingCourse.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['course_type', 'status', 'department', 'has_assessment', 'is_mandatory']
    search_fields = ['title', 'description', 'course_id']
    ordering_fields = ['title', 'created_at', 'duration_hours']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TrainingCourseDetailSerializer
        elif self.action == 'create':
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

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Change course status from draft to active"""
        course = self.get_object()
        if course.status == 'draft':
            course.status = 'active'
            course.updated_by = request.user
            course.save()
            return Response({
                'success': True,
                'message': f'Course "{course.title}" published successfully',
                'course': TrainingCourseDetailSerializer(course).data
            })
        return Response({
            'error': f'Cannot publish course with status "{course.get_status_display()}"'
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Change course status to archived"""
        course = self.get_object()
        course.status = 'archived'
        course.updated_by = request.user
        course.save()
        return Response({
            'success': True,
            'message': f'Course "{course.title}" archived successfully',
            'course': TrainingCourseDetailSerializer(course).data
        })

    @action(detail=True, methods=['post'])
    def assign_users(self, request, pk=None):
        """Bulk assign course to list of user IDs"""
        course = self.get_object()
        user_ids = request.data.get('user_ids', [])
        due_date = request.data.get('due_date')

        if not user_ids:
            return Response({
                'error': 'user_ids list is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not due_date:
            return Response({
                'error': 'due_date is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            assigned_count = 0
            users = User.objects.filter(id__in=user_ids)

            for user in users:
                assignment, created = TrainingAssignment.objects.get_or_create(
                    user=user,
                    course=course,
                    defaults={
                        'due_date': due_date,
                        'assigned_by': request.user,
                        'created_by': request.user,
                        'updated_by': request.user,
                        'status': 'not_started'
                    }
                )
                if created:
                    assigned_count += 1

            return Response({
                'success': True,
                'message': f'{assigned_count} users assigned to "{course.title}"',
                'course_id': course.id,
                'assigned_count': assigned_count,
                'total_users': len(user_ids)
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def auto_assign(self, request, pk=None):
        """Auto-assign course to all users with matching job_function"""
        course = self.get_object()
        job_function_id = request.data.get('job_function_id')
        due_date = request.data.get('due_date')

        if not job_function_id:
            return Response({
                'error': 'job_function_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not due_date:
            return Response({
                'error': 'due_date is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            job_function = JobFunction.objects.get(id=job_function_id)
            users = User.objects.filter(
                profile__job_function=job_function
            ).exclude(
                training_assignments__course=course
            ).distinct()

            assigned_count = 0
            for user in users:
                assignment, created = TrainingAssignment.objects.get_or_create(
                    user=user,
                    course=course,
                    defaults={
                        'due_date': due_date,
                        'assigned_by': request.user,
                        'created_by': request.user,
                        'updated_by': request.user,
                        'status': 'not_started'
                    }
                )
                if created:
                    assigned_count += 1

            return Response({
                'success': True,
                'message': f'{assigned_count} users auto-assigned to "{course.title}"',
                'course_id': course.id,
                'assigned_count': assigned_count,
                'job_function': job_function.name
            }, status=status.HTTP_201_CREATED)
        except JobFunction.DoesNotExist:
            return Response({
                'error': 'Job function not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def course_stats(self, request, pk=None):
        """Get course statistics: completion rate, avg score, pass rate"""
        course = self.get_object()
        assignments = course.assignments.all()
        total = assignments.count()

        if total == 0:
            return Response({
                'course_id': course.id,
                'course_title': course.title,
                'total_assigned': 0,
                'completion_rate': 0,
                'avg_score': None,
                'pass_rate': 0,
                'status_breakdown': {}
            })

        completed = assignments.filter(status='completed').count()
        completion_rate = (completed / total * 100) if total > 0 else 0

        avg_score = assignments.filter(
            score__isnull=False
        ).aggregate(avg=Avg('score'))['avg']

        passed = assignments.filter(
            status='completed',
            score__gte=course.passing_score_percent
        ).count()
        pass_rate = (passed / completed * 100) if completed > 0 else 0

        status_breakdown = assignments.values('status').annotate(
            count=Count('id')
        ).order_by('status')

        return Response({
            'course_id': course.id,
            'course_title': course.title,
            'total_assigned': total,
            'completed': completed,
            'completion_rate': round(completion_rate, 2),
            'avg_score': round(avg_score, 2) if avg_score else None,
            'passed': passed,
            'pass_rate': round(pass_rate, 2),
            'status_breakdown': list(status_breakdown)
        })


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
    """ViewSet for training assignments with enhanced filtering and actions"""
    queryset = TrainingAssignment.objects.select_related('user', 'course')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'user', 'course']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'course__title']
    ordering_fields = ['assigned_date', 'due_date', 'status', 'completion_date']
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
    def my_training(self, request):
        """Get current user's assigned training"""
        assignments = self.queryset.filter(user=request.user).order_by('-due_date')

        page = self.paginate_queryset(assignments)
        if page is not None:
            serializer = TrainingAssignmentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TrainingAssignmentListSerializer(assignments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue training records"""
        today = timezone.now().date()
        overdue = self.queryset.filter(
            Q(status__in=['not_started', 'in_progress']) & Q(due_date__lt=today)
        ).order_by('due_date')

        page = self.paginate_queryset(overdue)
        if page is not None:
            serializer = TrainingAssignmentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TrainingAssignmentListSerializer(overdue, many=True)
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
                assignment.status = 'completed'
                assignment.completion_date = timezone.now()
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
        """Mark training assignment as complete with score and completion_date"""
        assignment = self.get_object()
        score = request.data.get('score')
        completion_date = request.data.get('completion_date', timezone.now())

        assignment.status = 'completed'
        assignment.completion_date = completion_date
        if score is not None:
            assignment.score = score
        assignment.updated_by = request.user
        assignment.save()

        return Response(
            TrainingAssignmentDetailSerializer(assignment).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'])
    def bulk_assign(self, request):
        """Create training records for multiple users"""
        user_ids = request.data.get('user_ids', [])
        course_id = request.data.get('course_id')
        due_date = request.data.get('due_date')

        if not user_ids or not course_id or not due_date:
            return Response({
                'error': 'user_ids, course_id, and due_date are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            course = TrainingCourse.objects.get(id=course_id)
            users = User.objects.filter(id__in=user_ids)
            created_count = 0

            for user in users:
                assignment, created = TrainingAssignment.objects.get_or_create(
                    user=user,
                    course=course,
                    defaults={
                        'due_date': due_date,
                        'assigned_by': request.user,
                        'created_by': request.user,
                        'updated_by': request.user,
                        'status': 'not_started'
                    }
                )
                if created:
                    created_count += 1

            return Response({
                'success': True,
                'message': f'{created_count} training records created',
                'created_count': created_count,
                'total_users': len(user_ids)
            }, status=status.HTTP_201_CREATED)
        except TrainingCourse.DoesNotExist:
            return Response({
                'error': 'Course not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class TrainingAssessmentViewSet(viewsets.ModelViewSet):
    """ViewSet for training assessments with full CRUD"""
    queryset = TrainingAssessment.objects.all()
    serializer_class = TrainingAssessmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['course', 'assessment_type']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """Set created_by and updated_by to current user on creation."""
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        """Set updated_by to current user on update."""
        serializer.save(updated_by=self.request.user)


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

        # Mandatory = courses linked to mandatory training plans (via TrainingPlanCourse)
        from .models import TrainingPlanCourse
        mandatory_course_ids = TrainingPlanCourse.objects.filter(
            training_plan__is_mandatory=True
        ).values_list('course_id', flat=True)
        mandatory_assignments = TrainingAssignment.objects.filter(course_id__in=mandatory_course_ids)
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
        # Get all assignments with related user data
        assignments = TrainingAssignment.objects.select_related('user')

        dept_stats = {}
        today = timezone.now().date()

        for assignment in assignments:
            # Get department from user if available
            dept_name = 'Unassigned'
            if hasattr(assignment.user, 'profile') and assignment.user.profile.department:
                dept_name = assignment.user.profile.department.name

            if dept_name not in dept_stats:
                dept_stats[dept_name] = {
                    'total': 0,
                    'completed': 0,
                    'overdue': 0
                }

            dept_stats[dept_name]['total'] += 1
            if assignment.status == 'completed':
                dept_stats[dept_name]['completed'] += 1
            if assignment.status in ['assigned', 'in_progress'] and assignment.due_date.date() < today:
                dept_stats[dept_name]['overdue'] += 1

        data = []
        for dept_name, stats in sorted(dept_stats.items()):
            total = stats['total']
            completed = stats['completed']
            compliance_pct = (completed / total * 100) if total > 0 else 0
            data.append({
                'department': dept_name,
                'total': total,
                'completed': completed,
                'overdue': stats['overdue'],
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

                # Get required courses for job function (via mandatory training plans)
                courses = TrainingCourse.objects.filter(
                    applicable_job_functions=job_function
                )

                # Auto-assign courses to users in department with this job function
                from django.contrib.auth import get_user_model
                User = get_user_model()

                assigned_count = 0
                for course in courses:
                    users = User.objects.filter(
                        profile__department=department
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


class TrainingDashboardView(APIView):
    """APIView for training dashboard with key metrics"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get comprehensive training dashboard data"""
        today = timezone.now().date()

        # Total counts
        total_courses = TrainingCourse.objects.filter(status='active').count()
        total_assignments = TrainingAssignment.objects.count()

        # Completion metrics
        completed_assignments = TrainingAssignment.objects.filter(
            status='completed'
        ).count()
        completion_rate = (completed_assignments / total_assignments * 100) if total_assignments > 0 else 0

        # Overdue metrics
        overdue_count = TrainingAssignment.objects.filter(
            Q(status__in=['not_started', 'in_progress']) & Q(due_date__lt=today)
        ).count()

        # Compliance by department
        from users.models import Department
        departments = Department.objects.all()
        compliance_by_department = []

        for dept in departments:
            dept_assignments = TrainingAssignment.objects.filter(
                user__profile__department=dept
            )
            dept_total = dept_assignments.count()
            dept_completed = dept_assignments.filter(status='completed').count()
            dept_rate = (dept_completed / dept_total * 100) if dept_total > 0 else 0

            compliance_by_department.append({
                'department': dept.name,
                'department_id': dept.id,
                'total': dept_total,
                'completed': dept_completed,
                'rate': round(dept_rate, 2)
            })

        # Upcoming renewals (courses expiring in next 30 days)
        from_date = today
        to_date = today + timezone.timedelta(days=30)
        upcoming_renewals = TrainingAssignment.objects.filter(
            expiry_date__gte=from_date,
            expiry_date__lte=to_date
        ).select_related('user', 'course').values('user', 'course').distinct()

        upcoming_count = upcoming_renewals.count()

        return Response({
            'total_courses': total_courses,
            'total_assignments': total_assignments,
            'completed_assignments': completed_assignments,
            'completion_rate': round(completion_rate, 2),
            'overdue_count': overdue_count,
            'upcoming_renewals': upcoming_count,
            'compliance_by_department': sorted(
                compliance_by_department,
                key=lambda x: x['rate'],
                reverse=True
            )
        })
