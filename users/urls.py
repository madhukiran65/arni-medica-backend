from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet,
    RoleViewSet,
    UserProfileViewSet,
    CurrentUserView,
    SiteViewSet,
    ProductLineViewSet
)

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'sites', SiteViewSet, basename='site')
router.register(r'product-lines', ProductLineViewSet, basename='product-line')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'profiles', UserProfileViewSet, basename='userprofile')
router.register(r'current-user', CurrentUserView, basename='current-user')

app_name = 'users'

urlpatterns = [
    path('', include(router.urls)),
]
