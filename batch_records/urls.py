from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MasterBatchRecordViewSet,
    BatchRecordViewSet,
    BatchStepViewSet,
    BatchDeviationViewSet,
    BatchMaterialViewSet,
    BatchEquipmentViewSet,
)

app_name = 'batch_records'

router = DefaultRouter()
router.register(
    r'master-batch-records',
    MasterBatchRecordViewSet,
    basename='master-batch-record'
)
router.register(
    r'batch-records',
    BatchRecordViewSet,
    basename='batch-record'
)
router.register(
    r'batch-steps',
    BatchStepViewSet,
    basename='batch-step'
)
router.register(
    r'batch-deviations',
    BatchDeviationViewSet,
    basename='batch-deviation'
)
router.register(
    r'batch-materials',
    BatchMaterialViewSet,
    basename='batch-material'
)
router.register(
    r'batch-equipment',
    BatchEquipmentViewSet,
    basename='batch-equipment'
)

urlpatterns = [
    path('', include(router.urls)),
]
