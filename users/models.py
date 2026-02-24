from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Department(models.Model):
    """Department model for organizing users"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
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
    
    # Granular permissions
    can_create_documents = models.BooleanField(default=False)
    can_approve_documents = models.BooleanField(default=False)
    can_sign_documents = models.BooleanField(default=False)
    can_create_capa = models.BooleanField(default=False)
    can_close_capa = models.BooleanField(default=False)
    can_create_complaints = models.BooleanField(default=False)
    can_log_training = models.BooleanField(default=False)
    can_create_audit = models.BooleanField(default=False)
    can_view_audit_trail = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    
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
    department = models.ForeignKey(
        Department,
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
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"
