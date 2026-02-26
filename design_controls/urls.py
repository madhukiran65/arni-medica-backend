from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DesignProjectViewSet,
    UserNeedViewSet,
    DesignInputViewSet,
    DesignOutputViewSet,
    VVProtocolViewSet,
    DesignReviewViewSet,
    DesignTransferViewSet,
    TraceabilityLinkViewSet,
)

router = DefaultRouter()
router.register(r'design-projects', DesignProjectViewSet, basename='design-project')
router.register(r'user-needs', UserNeedViewSet, basename='user-need')
router.register(r'design-inputs', DesignInputViewSet, basename='design-input')
router.register(r'design-outputs', DesignOutputViewSet, basename='design-output')
router.register(r'vv-protocols', VVProtocolViewSet, basename='vv-protocol')
router.register(r'design-reviews', DesignReviewViewSet, basename='design-review')
router.register(r'design-transfers', DesignTransferViewSet, basename='design-transfer')
router.register(r'traceability-links', TraceabilityLinkViewSet, basename='traceability-link')

urlpatterns = [
    path('', include(router.urls)),
]
