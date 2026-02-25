from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'definitions', views.WorkflowDefinitionViewSet, basename='workflow-definition')
router.register(r'records', views.WorkflowRecordViewSet, basename='workflow-record')
router.register(r'approvals', views.WorkflowApprovalRequestViewSet, basename='workflow-approval')
router.register(r'delegations', views.WorkflowDelegationViewSet, basename='workflow-delegation')
router.register(r'pending-actions', views.PendingActionsViewSet, basename='pending-actions')

urlpatterns = [
    path('', include(router.urls)),
]
