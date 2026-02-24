from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrainingCourseViewSet, TrainingAssignmentViewSet

router = DefaultRouter()
router.register(r'courses', TrainingCourseViewSet, basename='training-course')
router.register(r'assignments', TrainingAssignmentViewSet, basename='training-assignment')

urlpatterns = [
    path('', include(router.urls)),
]
