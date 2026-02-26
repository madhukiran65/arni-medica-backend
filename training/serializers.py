from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from decimal import Decimal

from .models import (
    JobFunction,
    TrainingCourse,
    TrainingPlan,
    TrainingPlanCourse,
    TrainingAssignment,
    TrainingAssessment,
    TrainingCompetency,
    AssessmentQuestion,
    AssessmentAttempt,
    AssessmentResponse,
    TrainingComplianceRecord,
)


# ============================================================================
# USER SERIALIZER
# ============================================================================
class UserSerializer(serializers.ModelSerializer):
    """Basic user information"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'full_name']
        read_only_fields = ['id']


# ============================================================================
# JOB FUNCTION SERIALIZERS
# ============================================================================
class JobFunctionSerializer(serializers.ModelSerializer):
    """Job function with hierarchy information"""
    children_count = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = JobFunction
        fields = [
            'id', 'code', 'name', 'description', 'parent', 'parent_name',
            'department', 'department_name', 'is_active', 'children_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_children_count(self, obj):
        return obj.children.count()


# ============================================================================
# TRAINING COMPETENCY SERIALIZERS
# ============================================================================
class TrainingCompetencySerializer(serializers.ModelSerializer):
    """Training competency details"""
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = TrainingCompetency
        fields = [
            'id', 'name', 'description', 'course', 'course_title',
            'is_mandatory', 'renewal_period_months', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ============================================================================
# TRAINING COURSE SERIALIZERS
# ============================================================================
class TrainingCourseListSerializer(serializers.ModelSerializer):
    """Compact training course list view"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    assignments_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    course_type_display = serializers.CharField(source='get_course_type_display', read_only=True)

    class Meta:
        model = TrainingCourse
        fields = [
            'id', 'course_id', 'title', 'course_type', 'course_type_display',
            'status', 'status_display', 'duration_hours', 'category',
            'has_assessment', 'department', 'department_name', 'assignments_count'
        ]
        read_only_fields = ['id']

    def get_assignments_count(self, obj):
        return obj.assignments.count()


class TrainingCourseDetailSerializer(serializers.ModelSerializer):
    """Full training course details with prerequisites and job functions"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    trainer_name = serializers.CharField(source='trainer.get_full_name', read_only=True)
    prerequisites = TrainingCourseListSerializer(many=True, read_only=True)
    applicable_job_functions = JobFunctionSerializer(many=True, read_only=True)
    dependent_courses_count = serializers.SerializerMethodField()
    assignments_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    course_type_display = serializers.CharField(source='get_course_type_display', read_only=True)
    competencies = TrainingCompetencySerializer(many=True, read_only=True)

    class Meta:
        model = TrainingCourse
        fields = [
            'id', 'course_id', 'title', 'description', 'course_type', 'course_type_display',
            'category', 'status', 'status_display', 'duration_hours', 'renewal_required',
            'renewal_frequency_months', 'has_assessment', 'passing_score_percent',
            'max_attempts', 'scorm_package_url', 'course_material', 'version',
            'effective_date', 'expiry_date', 'regulatory_requirement', 'trainer',
            'trainer_name', 'department', 'department_name', 'prerequisites',
            'applicable_job_functions', 'auto_assign_on_role_change', 'competencies',
            'dependent_courses_count', 'assignments_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_dependent_courses_count(self, obj):
        return obj.dependent_courses.count()

    def get_assignments_count(self, obj):
        return obj.assignments.count()


# ============================================================================
# TRAINING PLAN SERIALIZERS
# ============================================================================
class TrainingPlanCourseSerializer(serializers.ModelSerializer):
    """Training plan course with course details"""
    course_details = TrainingCourseListSerializer(source='course', read_only=True)

    class Meta:
        model = TrainingPlanCourse
        fields = ['id', 'course', 'course_details', 'sequence', 'days_until_due', 'is_required']
        read_only_fields = ['id']


class TrainingPlanSerializer(serializers.ModelSerializer):
    """Training plan with nested courses"""
    job_function_name = serializers.CharField(source='job_function.name', read_only=True)
    courses = TrainingPlanCourseSerializer(many=True, read_only=True)
    courses_count = serializers.SerializerMethodField()

    class Meta:
        model = TrainingPlan
        fields = [
            'id', 'name', 'description', 'job_function', 'job_function_name',
            'is_active', 'is_mandatory', 'courses', 'courses_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_courses_count(self, obj):
        return obj.courses.count()


# ============================================================================
# TRAINING ASSIGNMENT SERIALIZERS
# ============================================================================
class TrainingAssignmentListSerializer(serializers.ModelSerializer):
    """Compact training assignment list"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_id = serializers.CharField(source='course.course_id', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    days_overdue = serializers.SerializerMethodField()

    class Meta:
        model = TrainingAssignment
        fields = [
            'id', 'user', 'user_name', 'course', 'course_id', 'course_title',
            'status', 'status_display', 'due_date', 'score', 'days_overdue'
        ]
        read_only_fields = ['id']

    def get_days_overdue(self, obj):
        if obj.status in ['completed', 'failed', 'waived']:
            return None

        today = timezone.now().date()
        if today > obj.due_date.date() if hasattr(obj.due_date, 'date') else today > obj.due_date:
            due_date = obj.due_date.date() if hasattr(obj.due_date, 'date') else obj.due_date
            return (today - due_date).days
        return 0


class AssessmentResponseSerializer(serializers.ModelSerializer):
    """Assessment response details"""
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    question_type = serializers.CharField(source='question.question_type', read_only=True)

    class Meta:
        model = AssessmentResponse
        fields = [
            'id', 'question', 'question_text', 'question_type',
            'response_text', 'selected_options', 'is_correct',
            'points_earned', 'answered_at'
        ]
        read_only_fields = ['id', 'answered_at']


class AssessmentAttemptSerializer(serializers.ModelSerializer):
    """Assessment attempt with response history"""
    assessment_title = serializers.CharField(source='assessment.title', read_only=True)
    responses = AssessmentResponseSerializer(many=True, read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    passed_display = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentAttempt
        fields = [
            'id', 'assessment', 'assessment_title', 'started_at', 'completed_at',
            'score', 'passed', 'passed_display', 'attempt_number', 'duration_minutes',
            'responses'
        ]
        read_only_fields = ['id']

    def get_duration_minutes(self, obj):
        if obj.completed_at and obj.started_at:
            delta = obj.completed_at - obj.started_at
            return int(delta.total_seconds() / 60)
        return None

    def get_passed_display(self, obj):
        if obj.passed is None:
            return 'In Progress'
        return 'Passed' if obj.passed else 'Failed'


class TrainingAssignmentDetailSerializer(serializers.ModelSerializer):
    """Full training assignment with attempt history"""
    user_details = UserSerializer(source='user', read_only=True)
    course_details = TrainingCourseListSerializer(source='course', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    trainer_verified_by_name = serializers.CharField(source='trainer_verified_by.get_full_name', read_only=True)
    training_plan_name = serializers.CharField(source='training_plan.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    assessment_attempts = AssessmentAttemptSerializer(many=True, read_only=True)
    days_overdue = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()

    class Meta:
        model = TrainingAssignment
        fields = [
            'id', 'user', 'user_details', 'course', 'course_details',
            'assigned_date', 'due_date', 'completion_date', 'status', 'status_display',
            'assigned_by', 'assigned_by_name', 'training_plan', 'training_plan_name',
            'attempt_count', 'score', 'time_spent_minutes', 'completion_evidence',
            'trainer_verification', 'trainer_verified_by', 'trainer_verified_by_name',
            'trainer_verified_at', 'certificate_issued', 'certificate_number',
            'expiry_date', 'notes', 'days_overdue', 'time_remaining',
            'assessment_attempts', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_days_overdue(self, obj):
        if obj.status in ['completed', 'failed', 'waived']:
            return None

        today = timezone.now().date()
        due_date = obj.due_date.date() if hasattr(obj.due_date, 'date') else obj.due_date
        if today > due_date:
            return (today - due_date).days
        return 0

    def get_time_remaining(self, obj):
        if obj.status in ['completed', 'failed', 'waived']:
            return None

        today = timezone.now().date()
        due_date = obj.due_date.date() if hasattr(obj.due_date, 'date') else obj.due_date
        if due_date > today:
            return (due_date - today).days
        return None


# ============================================================================
# TRAINING ASSESSMENT SERIALIZERS
# ============================================================================
class AssessmentQuestionSerializer(serializers.ModelSerializer):
    """Assessment question with options"""
    question_type_display = serializers.CharField(source='get_question_type_display', read_only=True)

    class Meta:
        model = AssessmentQuestion
        fields = [
            'id', 'assessment', 'question_text', 'question_type', 'question_type_display',
            'options', 'correct_answer', 'points', 'sequence', 'explanation',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TrainingAssessmentSerializer(serializers.ModelSerializer):
    """Assessment with nested questions"""
    course_title = serializers.CharField(source='course.title', read_only=True)
    questions = AssessmentQuestionSerializer(many=True, read_only=True)
    questions_count = serializers.SerializerMethodField()
    total_points = serializers.SerializerMethodField()
    assessment_type_display = serializers.CharField(source='get_assessment_type_display', read_only=True)

    class Meta:
        model = TrainingAssessment
        fields = [
            'id', 'course', 'course_title', 'title', 'description', 'assessment_type',
            'assessment_type_display', 'passing_score', 'time_limit_minutes', 'max_attempts',
            'randomize_questions', 'show_correct_answers', 'is_active', 'questions',
            'questions_count', 'total_points', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_questions_count(self, obj):
        return obj.questions.count()

    def get_total_points(self, obj):
        return obj.questions.aggregate(
            total=models.Sum('points')
        )['total'] or 0


# ============================================================================
# COMPLIANCE SERIALIZERS
# ============================================================================
class TrainingComplianceRecordSerializer(serializers.ModelSerializer):
    """Training compliance record"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    remaining_courses = serializers.SerializerMethodField()

    class Meta:
        model = TrainingComplianceRecord
        fields = [
            'id', 'user', 'user_name', 'department', 'department_name',
            'total_required', 'total_completed', 'total_overdue',
            'compliance_percentage', 'remaining_courses', 'period_start',
            'period_end', 'last_calculated', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_calculated', 'created_at', 'updated_at']

    def get_remaining_courses(self, obj):
        return obj.total_required - obj.total_completed


# ============================================================================
# ACTION SERIALIZERS
# ============================================================================
class SubmitAssessmentSerializer(serializers.Serializer):
    """Action serializer for submitting assessment responses"""
    responses = serializers.ListField(
        child=serializers.JSONField(),
        help_text="List of {question_id, response_text, selected_options}"
    )


class AssignTrainingSerializer(serializers.Serializer):
    """Action serializer for assigning training to multiple users"""
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of user IDs"
    )
    course_id = serializers.IntegerField()
    due_date = serializers.DateTimeField()
