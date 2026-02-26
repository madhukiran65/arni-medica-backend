from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Department, Role, UserProfile, Site, ProductLine


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'description', 'head', 'parent',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = [
            'id', 'name', 'code', 'address', 'city', 'state', 'country',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProductLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductLine
        fields = [
            'id', 'name', 'code', 'description', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = [
            'id',
            'name',
            'description',
            # Document Control permissions
            'can_create_documents',
            'can_approve_documents',
            'can_sign_documents',
            'can_release_documents',
            'can_obsolete_documents',
            # CAPA permissions
            'can_create_capa',
            'can_approve_capa',
            'can_close_capa',
            # Complaint permissions
            'can_create_complaints',
            'can_investigate_complaints',
            # Deviation permissions
            'can_create_deviations',
            'can_approve_deviations',
            # Change Control permissions
            'can_create_change_controls',
            'can_approve_change_controls',
            # Training permissions
            'can_log_training',
            'can_assign_training',
            'can_create_courses',
            # Audit permissions
            'can_create_audit',
            'can_lead_audit',
            # Supplier permissions
            'can_manage_suppliers',
            'can_qualify_suppliers',
            # Form permissions
            'can_create_forms',
            'can_publish_forms',
            # Admin permissions
            'can_view_audit_trail',
            'can_manage_users',
            'can_manage_settings',
            'can_manage_workflows',
            'can_export_data',
            # Status
            'is_active',
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
    site = SiteSerializer(read_only=True)
    site_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    roles = RoleSerializer(many=True, read_only=True)
    role_ids = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='roles'
    )
    job_function_name = serializers.CharField(source='job_function.name', read_only=True, allow_null=True)
    supervisor_name = serializers.CharField(source='supervisor.get_full_name', read_only=True, allow_null=True)

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user',
            'employee_id',
            'title',
            'phone',
            'first_name',
            'last_name',
            'email',
            'username',
            'department',
            'department_id',
            'site',
            'site_id',
            'roles',
            'role_ids',
            'job_function',
            'job_function_name',
            'supervisor',
            'supervisor_name',
            'date_of_joining',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        department_id = validated_data.pop('department_id', None)
        site_id = validated_data.pop('site_id', None)
        if department_id is not None:
            instance.department_id = department_id
        if site_id is not None:
            instance.site_id = site_id
        return super().update(instance, validated_data)


class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    password = serializers.CharField(write_only=True, min_length=8)
    employee_id = serializers.CharField(max_length=50)
    department_id = serializers.IntegerField(required=False, allow_null=True)
    site_id = serializers.IntegerField(required=False, allow_null=True)
    title = serializers.CharField(max_length=100, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=30, required=False, allow_blank=True)
    role_ids = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        many=True,
        required=False
    )

    def create(self, validated_data):
        # Extract non-User fields
        employee_id = validated_data.pop('employee_id')
        department_id = validated_data.pop('department_id', None)
        site_id = validated_data.pop('site_id', None)
        title = validated_data.pop('title', '')
        phone = validated_data.pop('phone', '')
        role_ids = validated_data.pop('role_ids', [])

        # Create User
        user = User.objects.create_user(**validated_data)

        # Create UserProfile
        profile = UserProfile.objects.create(
            user=user,
            employee_id=employee_id,
            department_id=department_id,
            site_id=site_id,
            title=title,
            phone=phone
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


class UserManagementSerializer(serializers.Serializer):
    """Admin-focused serializer for creating/updating users with full profile"""
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8, required=False)
    employee_id = serializers.CharField(max_length=50)
    title = serializers.CharField(max_length=100, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=30, required=False, allow_blank=True)
    department_id = serializers.IntegerField(required=False, allow_null=True)
    site_id = serializers.IntegerField(required=False, allow_null=True)
    role_ids = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        many=True,
        required=False
    )
    date_of_joining = serializers.DateField(required=False, allow_null=True)
    is_active = serializers.BooleanField(default=True)

    def create(self, validated_data):
        # Extract non-User fields
        employee_id = validated_data.pop('employee_id')
        department_id = validated_data.pop('department_id', None)
        site_id = validated_data.pop('site_id', None)
        title = validated_data.pop('title', '')
        phone = validated_data.pop('phone', '')
        role_ids = validated_data.pop('role_ids', [])
        date_of_joining = validated_data.pop('date_of_joining', None)
        is_active = validated_data.pop('is_active', True)

        # Create User
        user = User.objects.create_user(**validated_data)

        # Create UserProfile
        profile = UserProfile.objects.create(
            user=user,
            employee_id=employee_id,
            department_id=department_id,
            site_id=site_id,
            title=title,
            phone=phone,
            date_of_joining=date_of_joining,
            is_active=is_active
        )
        if role_ids:
            profile.roles.set(role_ids)

        return profile

    def update(self, instance, validated_data):
        # Update user fields
        user = instance.user
        user.first_name = validated_data.get('first_name', user.first_name)
        user.last_name = validated_data.get('last_name', user.last_name)
        user.email = validated_data.get('email', user.email)
        if 'password' in validated_data:
            user.set_password(validated_data['password'])
        user.save()

        # Update profile fields
        instance.title = validated_data.get('title', instance.title)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.department_id = validated_data.get('department_id', instance.department_id)
        instance.site_id = validated_data.get('site_id', instance.site_id)
        instance.date_of_joining = validated_data.get('date_of_joining', instance.date_of_joining)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        role_ids = validated_data.get('role_ids', None)
        if role_ids is not None:
            instance.roles.set(role_ids)

        return instance

    def validate_username(self, value):
        if User.objects.filter(username=value).exclude(username=self.instance.user.username if self.instance else None).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exclude(email=self.instance.user.email if self.instance else None).exists():
            raise serializers.ValidationError("Email already exists.")
        return value
