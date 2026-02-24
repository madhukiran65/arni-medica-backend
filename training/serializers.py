from rest_framework import serializers
from django.contrib.auth.models import User
from .models import TrainingCourse, TrainingAssignment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class TrainingCourseSerializer(serializers.ModelSerializer):
    assignments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TrainingCourse
        fields = [
            'id', 'course_id', 'title', 'description', 'course_type',
            'duration_hours', 'renewal_frequency_months', 'is_mandatory',
            'regulatory_requirement', 'assignments_count'
        ]
        read_only_fields = ['id']

    def get_assignments_count(self, obj):
        return obj.assignments.count()


class TrainingAssignmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    days_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = TrainingAssignment
        fields = [
            'id', 'course', 'course_title', 'assigned_to', 'assigned_to_name',
            'assigned_by', 'assigned_by_name', 'due_date', 'completion_date',
            'status', 'score', 'passed', 'days_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_days_overdue(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        
        if obj.status in ['completed', 'failed']:
            return None
        
        today = timezone.now().date()
        if today > obj.due_date:
            return (today - obj.due_date).days
        return 0


class ComplianceDashboardSerializer(serializers.Serializer):
    total_assignments = serializers.IntegerField()
    completed_assignments = serializers.IntegerField()
    overdue_assignments = serializers.IntegerField()
    failed_assignments = serializers.IntegerField()
    compliance_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    mandatory_compliance_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
