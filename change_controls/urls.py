from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChangeControlViewSet

router = DefaultRouter()
router.register(r'change-controls', ChangeControlViewSet, basename='change-control')

urlpatterns = [
    path('', include(router.urls)),
]
