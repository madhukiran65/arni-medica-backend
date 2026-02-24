from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Department, Role, UserProfile


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = [
            'id',
            'name',
            'description',
            'can_create_documents',
            'can_approve_documents',
            'can_sign_documents',
            'can_create_capa',
            'can_close_capa',
            'can_create_complaints',
            'can_log_training',
            'can_create_audit',
            'can_view_audit_trail',
            'can_manage_users',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    roles = RoleSerializer(many=True, read_only=True)
    role_ids = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='roles'
    )

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user',
            'employee_id',
            'first_name',
            'last_name',
            'email',
            'username',
            'department',
            'department_id',
            'roles',
            'role_ids',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        department_id = validated_data.pop('department_id', None)
        if department_id is not None:
            instance.department_id = department_id
        return super().update(instance, validated_data)


class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    password = serializers.CharField(write_only=True, min_length=8)
    employee_id = serializers.CharField(max_length=50)
    department_id = serializers.IntegerField(required=False, allow_null=True)
    role_ids = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        many=True,
        required=False
    )

    def create(self, validated_data):
        # Extract non-User fields
        employee_id = validated_data.pop('employee_id')
        department_id = validated_data.pop('department_id', None)
        role_ids = validated_data.pop('role_ids', [])

        # Create User
        user = User.objects.create_user(**validated_data)

        # Create UserProfile
        profile = UserProfile.objects.create(
            user=user,
            employee_id=employee_id,
            department_id=department_id
        )
        if role_ids:
            profile.roles.set(role_ids)

        return profile

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate_employee_id(self, value):
        if UserProfile.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError("Employee ID already exists.")
        return value
