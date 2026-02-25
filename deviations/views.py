from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from .models import Deviation, DeviationAttachment, DeviationComment
from .serializers import (
    DeviationListSerializer, DeviationDetailSerializer,
    DeviationCreateSerializer,
    DeviationAttachmentSerializer, DeviationCommentSerializer,
    StageTransitionSerializer
)


class DeviationViewSet(viewsets.ModelViewSet):
    """ViewSet for deviations with list/detail serializer pattern"""
    queryset = Deviation.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['current_stage', 'severity', 'category', 'deviation_type', 'department']
    search_fields = ['deviation_id', 'title', 'description']
    ordering_fields = ['created_at', 'severity', 'current_stage']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return DeviationCreateSerializer
        elif self.action == 'retrieve':
            return DeviationDetailSerializer
        return DeviationListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def stage_transition(self, request, pk=None):
        """Move deviation through workflow stages"""
        deviation = self.get_object()
        serializer = StageTransitionSerializer(data=request.data)

        if serializer.is_valid():
            try:
                target_stage = serializer.validated_data.get('target_stage')
                comments = serializer.validated_data.get('comments', '')

                # Validate stage transition is handled by serializer
                # Update stage
                deviation.current_stage = target_stage
                deviation.updated_by = request.user
                deviation.save()

                # Add comment about stage transition
                if comments:
                    DeviationComment.objects.create(
                        deviation=deviation,
                        author=request.user,
                        comment=f"Stage transitioned to {target_stage}: {comments}"
                    )

                return Response(
                    DeviationDetailSerializer(deviation).data,
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def attachments(self, request, pk=None):
        """Get or upload attachments for a deviation"""
        deviation = self.get_object()

        if request.method == 'GET':
            attachments = DeviationAttachment.objects.filter(deviation=deviation)
            serializer = DeviationAttachmentSerializer(attachments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'POST':
            serializer = DeviationAttachmentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    deviation=deviation,
                    uploaded_by=request.user
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """Get or add comments to a deviation"""
        deviation = self.get_object()

        if request.method == 'GET':
            comments = DeviationComment.objects.filter(deviation=deviation).order_by('-created_at')
            serializer = DeviationCommentSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'POST':
            serializer = DeviationCommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    deviation=deviation,
                    author=request.user
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def audit_trail(self, request, pk=None):
        """Get audit trail for a deviation"""
        deviation = self.get_object()

        audit_data = {
            'deviation_id': deviation.id,
            'created_by': deviation.created_by.username if deviation.created_by else None,
            'created_at': deviation.created_at,
            'updated_by': deviation.updated_by.username if deviation.updated_by else None,
            'updated_at': deviation.updated_at,
            'current_stage': deviation.current_stage,
            'severity': deviation.severity,
        }

        return Response(audit_data, status=status.HTTP_200_OK)
