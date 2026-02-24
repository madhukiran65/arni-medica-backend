from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User
from .models import Department, Role, UserProfile
from .serializers import (
    DepartmentSerializer,
    RoleSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer
)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
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
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response(
                {'detail': 'User profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


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
