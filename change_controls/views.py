from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .models import ChangeControl
from .serializers import (
    ChangeControlListSerializer,
    ChangeControlDetailSerializer,
    ChangeControlCreateSerializer,
    StageTransitionSerializer,
    ChangeControlApprovalSerializer,
    ApprovalResponseSerializer,
    ChangeControlTaskSerializer,
    ChangeControlAttachmentSerializer,
    ChangeControlCommentSerializer,
)


class ChangeControlViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Change Controls.
    Supports filtering, searching, and custom actions for workflow management.
    """
    queryset = ChangeControl.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['current_stage', 'change_type', 'change_category', 'risk_level', 'department']
    search_fields = ['change_control_id', 'title', 'description']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChangeControlDetailSerializer
        elif self.action == 'list':
            return ChangeControlListSerializer
        elif self.action == 'create':
            return ChangeControlCreateSerializer
        elif self.action == 'stage_transition':
            return StageTransitionSerializer
        elif self.action == 'respond_approval':
            return ApprovalResponseSerializer
        return ChangeControlDetailSerializer

    def perform_create(self, serializer):
        """Set created_by and updated_by to current user on creation."""
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        """Set updated_by to current user on update."""
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def stage_transition(self, request, pk=None):
        """
        Transition a change control to the next stage.
        """
        change_control = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Process stage transition logic here
        change_control.current_stage = serializer.validated_data['target_stage']
        change_control.save()
        
        return Response(
            ChangeControlDetailSerializer(change_control).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def approvals(self, request, pk=None):
        """
        Get all approvals for a change control.
        """
        change_control = self.get_object()
        approvals = change_control.approvals.all()
        serializer = ChangeControlApprovalSerializer(approvals, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def respond_approval(self, request, pk=None):
        """
        Respond to an approval request.
        """
        change_control = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Process approval response logic here
        
        return Response(
            ChangeControlDetailSerializer(change_control).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get', 'post'])
    def tasks(self, request, pk=None):
        """
        Get all tasks for a change control or create a new task.
        """
        change_control = self.get_object()
        
        if request.method == 'GET':
            tasks = change_control.tasks.all()
            serializer = ChangeControlTaskSerializer(tasks, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = ChangeControlTaskSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(change_control=change_control)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path=r'tasks/(?P<task_pk>\d+)/complete')
    def complete_task(self, request, pk=None, task_pk=None):
        """
        Mark a task as complete.
        """
        change_control = self.get_object()
        task = change_control.tasks.get(pk=task_pk)
        
        task.status = 'completed'
        task.save()
        
        serializer = ChangeControlTaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'post'])
    def attachments(self, request, pk=None):
        """
        Get all attachments for a change control or upload a new attachment.
        """
        change_control = self.get_object()
        
        if request.method == 'GET':
            attachments = change_control.attachments.all()
            serializer = ChangeControlAttachmentSerializer(attachments, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = ChangeControlAttachmentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(change_control=change_control)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """
        Get all comments for a change control or post a new comment.
        """
        change_control = self.get_object()
        
        if request.method == 'GET':
            comments = change_control.comments.all()
            serializer = ChangeControlCommentSerializer(comments, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = ChangeControlCommentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(change_control=change_control, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
