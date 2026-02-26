from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User
from django.db.models import Count
from .models import Department, Role, UserProfile, Site, ProductLine
from .serializers import (
    DepartmentSerializer,
    RoleSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    UserManagementSerializer,
    SiteSerializer,
    ProductLineSerializer
)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]


class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = [IsAuthenticated]


class ProductLineViewSet(viewsets.ModelViewSet):
    queryset = ProductLine.objects.all()
    serializer_class = ProductLineSerializer
    permission_classes = [IsAuthenticated]


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserManagementSerializer
        return UserProfileSerializer

    @action(detail=False, methods=['post'], permission_classes=[])
    def register(self, request):
        """Register a new user"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            profile = serializer.save()
            return Response(
                UserProfileSerializer(profile).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def current_user(self, request):
        """Get current user profile"""
        try:
            profile = request.user.profile
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response(
                {'detail': 'User profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
    def toggle_active(self, request, pk=None):
        """Toggle active status of a user (admin only)"""
        profile = self.get_object()
        profile.is_active = not profile.is_active
        profile.save()
        serializer = self.get_serializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
    def reset_password(self, request, pk=None):
        """Reset password for a user (admin only)"""
        profile = self.get_object()
        new_password = request.data.get('password')

        if not new_password:
            return Response(
                {'error': 'Password is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile.user.set_password(new_password)
        profile.user.save()

        return Response(
            {'success': True, 'message': f'Password reset for {profile.user.username}'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
    def update_roles(self, request, pk=None):
        """Update roles for a user (admin only)"""
        profile = self.get_object()
        role_ids = request.data.get('role_ids', [])

        if not isinstance(role_ids, list):
            return Response(
                {'error': 'role_ids must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            roles = Role.objects.filter(id__in=role_ids)
            profile.roles.set(roles)
            serializer = self.get_serializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsAdminUser])
    def users_by_department(self, request):
        """List users grouped by department (admin only)"""
        departments = Department.objects.prefetch_related('users').all()
        result = []

        for dept in departments:
            dept_users = []
            for profile in dept.users.all():
                dept_users.append({
                    'id': profile.id,
                    'employee_id': profile.employee_id,
                    'name': profile.user.get_full_name(),
                    'email': profile.user.email,
                    'is_active': profile.is_active
                })

            result.append({
                'department_id': dept.id,
                'department_name': dept.name,
                'user_count': len(dept_users),
                'users': dept_users
            })

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsAdminUser])
    def dashboard_stats(self, request):
        """Get user dashboard statistics (admin only)"""
        total_users = UserProfile.objects.count()
        active_users = UserProfile.objects.filter(is_active=True).count()
        inactive_users = UserProfile.objects.filter(is_active=False).count()

        # Users by department
        dept_stats = UserProfile.objects.values('department__name').annotate(
            count=Count('id')
        ).order_by('department__name')

        # Users by role
        role_stats = []
        for role in Role.objects.all():
            user_count = role.users.count()
            role_stats.append({
                'role_id': role.id,
                'role_name': role.name,
                'user_count': user_count
            })

        # Users by site
        site_stats = UserProfile.objects.values('site__name').annotate(
            count=Count('id')
        ).order_by('site__name')

        data = {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': inactive_users,
            'users_by_department': list(dept_stats),
            'users_by_role': role_stats,
            'users_by_site': list(site_stats)
        }

        return Response(data, status=status.HTTP_200_OK)


class CurrentUserView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current authenticated user and profile"""
        try:
            profile = request.user.profile
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response(
                {'detail': 'User profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
