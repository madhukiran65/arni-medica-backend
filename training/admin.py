from django.contrib import admin
from .models import (
    JobFunction, TrainingCourse, TrainingPlan, TrainingPlanCourse,
    TrainingAssignment, TrainingAssessment, AssessmentQuestion,
    AssessmentAttempt, AssessmentResponse, TrainingComplianceRecord
)


class TrainingPlanCourseInline(admin.TabularInline):
    model = TrainingPlanCourse
    fields = ('course', 'sequence', 'is_required')
    extra = 0


class AssessmentQuestionInline(admin.TabularInline):
    model = AssessmentQuestion
    fields = ('question_text', 'question_type', 'points', 'sequence')
    extra = 0


@admin.register(JobFunction)
class JobFunctionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department', 'is_active', 'created_at')
    list_filter = ('is_active', 'department', 'created_at')
    search_fields = ('code', 'name')
    ordering = ['name']


@admin.register(TrainingCourse)
class TrainingCourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'title', 'course_type', 'status', 'duration_hours')
    list_filter = ('status', 'course_type', 'renewal_required', 'created_at')
    search_fields = ('course_id', 'title', 'description')
    ordering = ['-created_at']


@admin.register(TrainingPlan)
class TrainingPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'job_function', 'is_active', 'is_mandatory', 'created_at')
    list_filter = ('is_active', 'is_mandatory', 'job_function', 'created_at')
    search_fields = ('name', 'description')
    ordering = ['-created_at']
    inlines = [TrainingPlanCourseInline]


@admin.register(TrainingPlanCourse)
class TrainingPlanCourseAdmin(admin.ModelAdmin):
    list_display = ('training_plan', 'course', 'sequence', 'is_required')
    list_filter = ('is_required', 'sequence')
    search_fields = ('training_plan__name', 'course__title')
    ordering = ['sequence']


@admin.register(TrainingAssignment)
class TrainingAssignmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'due_date', 'status', 'completion_date')
    list_filter = ('status', 'assigned_date', 'due_date', 'completion_date')
    search_fields = ('user__username', 'course__title')
    ordering = ['-assigned_date']


@admin.register(TrainingAssessment)
class TrainingAssessmentAdmin(admin.ModelAdmin):
    list_display = ('course', 'title', 'passing_score', 'time_limit_minutes')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    ordering = ['-created_at']
    inlines = [AssessmentQuestionInline]


@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(admin.ModelAdmin):
    list_display = ('assessment', 'question_type', 'points', 'sequence', 'is_active')
    list_filter = ('question_type', 'is_active', 'created_at')
    search_fields = ('assessment__title', 'question_text')
    ordering = ['sequence']


@admin.register(AssessmentAttempt)
class AssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'assessment', 'attempt_number', 'score', 'passed')
    list_filter = ('passed', 'started_at', 'completed_at')
    search_fields = ('assignment__user__username', 'assessment__title')
    ordering = ['-started_at']


@admin.register(AssessmentResponse)
class AssessmentResponseAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'is_correct', 'created_at')
    list_filter = ('is_correct', 'created_at')
    search_fields = ('attempt__assignment__user__username', 'question__question_text')
    ordering = ['-created_at']


@admin.register(TrainingComplianceRecord)
class TrainingComplianceRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'total_required', 'total_completed', 'compliance_percentage', 'last_calculated')
    list_filter = ('last_calculated', 'department')
    search_fields = ('user__username', 'department__name')
    ordering = ['-last_calculated']
