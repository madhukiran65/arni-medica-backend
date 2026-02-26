from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    DesignProject,
    UserNeed,
    DesignInput,
    DesignOutput,
    VVProtocol,
    DesignReview,
    DesignTransfer,
    TraceabilityLink,
)
from .serializers import (
    DesignProjectListSerializer,
    DesignProjectDetailSerializer,
    UserNeedListSerializer,
    UserNeedDetailSerializer,
    DesignInputListSerializer,
    DesignInputDetailSerializer,
    DesignOutputListSerializer,
    DesignOutputDetailSerializer,
    VVProtocolListSerializer,
    VVProtocolDetailSerializer,
    DesignReviewListSerializer,
    DesignReviewDetailSerializer,
    DesignTransferListSerializer,
    DesignTransferDetailSerializer,
    TraceabilityLinkSerializer,
)
from .filters import (
    DesignProjectFilterSet,
    UserNeedFilterSet,
    DesignInputFilterSet,
    DesignOutputFilterSet,
    VVProtocolFilterSet,
    DesignReviewFilterSet,
    DesignTransferFilterSet,
    TraceabilityLinkFilterSet,
)


class DesignProjectViewSet(viewsets.ModelViewSet):
    queryset = DesignProject.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DesignProjectFilterSet
    search_fields = ['project_id', 'title', 'description']
    ordering_fields = ['created_at', 'target_completion_date', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DesignProjectDetailSerializer
        return DesignProjectListSerializer

    @action(detail=True, methods=['get'])
    def traceability_report(self, request, pk=None):
        """Generate a traceability report for the project"""
        project = self.get_object()
        links = project.traceability_links.all()
        missing_links = links.filter(link_status='missing')

        return Response({
            'project_id': project.project_id,
            'total_links': links.count(),
            'complete_links': links.filter(link_status='complete').count(),
            'partial_links': links.filter(link_status='partial').count(),
            'missing_links': missing_links.count(),
            'missing_details': TraceabilityLinkSerializer(missing_links, many=True).data,
        })


class UserNeedViewSet(viewsets.ModelViewSet):
    queryset = UserNeed.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UserNeedFilterSet
    search_fields = ['need_id', 'description']
    ordering_fields = ['created_at', 'priority', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserNeedDetailSerializer
        return UserNeedListSerializer


class DesignInputViewSet(viewsets.ModelViewSet):
    queryset = DesignInput.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DesignInputFilterSet
    search_fields = ['input_id', 'specification']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DesignInputDetailSerializer
        return DesignInputListSerializer


class DesignOutputViewSet(viewsets.ModelViewSet):
    queryset = DesignOutput.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DesignOutputFilterSet
    search_fields = ['output_id', 'description']
    ordering_fields = ['created_at', 'status', 'revision']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DesignOutputDetailSerializer
        return DesignOutputListSerializer


class VVProtocolViewSet(viewsets.ModelViewSet):
    queryset = VVProtocol.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = VVProtocolFilterSet
    search_fields = ['protocol_id', 'title']
    ordering_fields = ['created_at', 'status', 'execution_date']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return VVProtocolDetailSerializer
        return VVProtocolListSerializer

    @action(detail=True, methods=['post'])
    def mark_executed(self, request, pk=None):
        """Mark a V&V protocol as executed"""
        protocol = self.get_object()
        protocol.status = 'executed'
        protocol.executed_by = request.user
        protocol.save()
        return Response(
            VVProtocolDetailSerializer(protocol).data,
            status=status.HTTP_200_OK
        )


class DesignReviewViewSet(viewsets.ModelViewSet):
    queryset = DesignReview.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DesignReviewFilterSet
    search_fields = ['review_id', 'phase']
    ordering_fields = ['created_at', 'review_date', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DesignReviewDetailSerializer
        return DesignReviewListSerializer


class DesignTransferViewSet(viewsets.ModelViewSet):
    queryset = DesignTransfer.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DesignTransferFilterSet
    search_fields = ['transfer_id']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DesignTransferDetailSerializer
        return DesignTransferListSerializer


class TraceabilityLinkViewSet(viewsets.ModelViewSet):
    queryset = TraceabilityLink.objects.all()
    serializer_class = TraceabilityLinkSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = TraceabilityLinkFilterSet
    ordering_fields = ['created_at', 'link_status']
    ordering = ['-created_at']
