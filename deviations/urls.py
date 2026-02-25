from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviationViewSet

router = DefaultRouter()
router.register(r'deviations', DeviationViewSet, basename='deviation')

urlpatterns = [
    path('', include(router.urls)),
]
