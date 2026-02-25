from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ComplaintViewSet,
    MIRRecordViewSet,
    MDRDashboardViewSet
)

router = DefaultRouter()
router.register(r'complaints', ComplaintViewSet, basename='complaint')
router.register(r'mir-records', MIRRecordViewSet, basename='mir-record')
router.register(r'mdr-dashboard', MDRDashboardViewSet, basename='mdr-dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
