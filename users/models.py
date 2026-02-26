from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Department(models.Model):
    """Department model for organizing users"""
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=20, unique=True, blank=True)
    description = models.TextField(blank=True)
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_departments'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Site(models.Model):
    """Manufacturing or office site"""
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=20, unique=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductLine(models.Model):
    """Product lines for the organization"""
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=20, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Role(models.Model):
    """Role model with granular permissions"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    # Document Control permissions
    can_create_documents = models.BooleanField(default=False)
    can_approve_documents = models.BooleanField(default=False)
    can_sign_documents = models.BooleanField(default=False)
    can_release_documents = models.BooleanField(default=False)
    can_obsolete_documents = models.BooleanField(default=False)

    # CAPA permissions
    can_create_capa = models.BooleanField(default=False)
    can_approve_capa = models.BooleanField(default=False)
    can_close_capa = models.BooleanField(default=False)

    # Complaint permissions
    can_create_complaints = models.BooleanField(default=False)
    can_investigate_complaints = models.BooleanField(default=False)

    # Deviation permissions
    can_create_deviations = models.BooleanField(default=False)
    can_approve_deviations = models.BooleanField(default=False)

    # Change Control permissions
    can_create_change_controls = models.BooleanField(default=False)
    can_approve_change_controls = models.BooleanField(default=False)

    # Training permissions
    can_log_training = models.BooleanField(default=False)
    can_assign_training = models.BooleanField(default=False)
    can_create_courses = models.BooleanField(default=False)

    # Audit permissions
    can_create_audit = models.BooleanField(default=False)
    can_lead_audit = models.BooleanField(default=False)

    # Supplier permissions
    can_manage_suppliers = models.BooleanField(default=False)
    can_qualify_suppliers = models.BooleanField(default=False)

    # Form permissions
    can_create_forms = models.BooleanField(default=False)
    can_publish_forms = models.BooleanField(default=False)

    # Admin permissions
    can_view_audit_trail = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    can_manage_settings = models.BooleanField(default=False)
    can_manage_workflows = models.BooleanField(default=False)
    can_export_data = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """Extended user profile with department and roles"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    employee_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    site = models.ForeignKey(
        Site,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    roles = models.ManyToManyField(
        Role,
        related_name='users',
        blank=True
    )
    job_function = models.ForeignKey(
        'training.JobFunction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_profiles'
    )
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='direct_reports'
    )
    date_of_joining = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"

    def has_permission(self, permission_name):
        """Check if user has a specific permission via any of their roles"""
        return self.roles.filter(**{permission_name: True}).exists()
