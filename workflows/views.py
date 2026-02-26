"""
Workflow Engine API ViewSets.
"""
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    WorkflowDefinition, WorkflowRecord,
    WorkflowApprovalRequest, WorkflowDelegation,
)
from .serializers import (
    WorkflowDefinitionSerializer, WorkflowDefinitionListSerializer,
    WorkflowRecordSerializer, WorkflowRecordDetailSerializer,
    WorkflowApprovalRequestSerializer,
    TransitionActionSerializer, ApprovalResponseSerializer,
    AddApproverSerializer, ExtendDeadlineSerializer,
    WorkflowDelegationSerializer,
)
from .services import (
    WorkflowService, WorkflowError, TransitionNotAllowed,
    ApprovalRequired, FieldValidationError, SignatureRequired,
)

User = get_user_model()


class WorkflowDefinitionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View workflow definitions (read-only).
    Only admins can modify workflow definitions (via Django admin).
    """
    queryset = WorkflowDefinition.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return WorkflowDefinitionListSerializer
        return WorkflowDefinitionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        model_type = self.request.query_params.get('model_type')
        if model_type:
            qs = qs.filter(model_type=model_type)
        return qs.prefetch_related('stages', 'transitions')


class WorkflowRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View and manage workflow records (state tracking for EQMS records).
    """
    queryset = WorkflowRecord.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return WorkflowRecordDetailSerializer
        return WorkflowRecordSerializer

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            'current_stage', 'workflow'
        )
        # Filter by model_type
        model_type = self.request.query_params.get('model_type')
        if model_type:
            qs = qs.filter(workflow__model_type=model_type)
        # Filter by stage
        stage_slug = self.request.query_params.get('stage')
        if stage_slug:
            qs = qs.filter(current_stage__slug=stage_slug)
        # Filter overdue
        overdue = self.request.query_params.get('overdue')
        if overdue == 'true':
            qs = qs.filter(is_overdue=True)
        return qs

    @action(detail=False, methods=['get'], url_path='by-record')
    def by_record(self, request):
        """
        Look up workflow record by model_type and object_id.
        Usage: GET /api/workflows/records/by-record/?model_type=document&object_id=123
        Returns full workflow state with stages, transitions, and approval status.
        """
        model_type = request.query_params.get('model_type')
        object_id = request.query_params.get('object_id')
        if not model_type or not object_id:
            return Response(
                {'error': 'model_type and object_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            wr = WorkflowRecord.objects.select_related(
                'current_stage', 'workflow'
            ).get(
                workflow__model_type=model_type,
                object_id=object_id,
                is_active=True,
            )
        except WorkflowRecord.DoesNotExist:
            return Response(
                {'error': 'No workflow record found', 'has_workflow': False},
                status=status.HTTP_200_OK
            )

        # Build comprehensive response
        all_stages = list(wr.workflow.stages.order_by('sequence').values(
            'id', 'name', 'slug', 'sequence', 'color', 'icon',
            'requires_approval', 'requires_signature', 'is_initial',
            'is_terminal', 'allows_edit', 'sla_days',
        ))
        transitions = WorkflowService.get_valid_transitions(wr)
        approval_status = WorkflowService.get_approval_status(wr)
        history = wr.history.order_by('-transitioned_at').values(
            'from_stage__name', 'to_stage__name', 'transitioned_by__username',
            'transitioned_at', 'comments', 'time_in_stage_seconds',
        )[:20]

        return Response({
            'has_workflow': True,
            'workflow_record_id': wr.id,
            'workflow_name': wr.workflow.name,
            'model_type': wr.workflow.model_type,
            'current_stage': {
                'id': wr.current_stage.id,
                'name': wr.current_stage.name,
                'slug': wr.current_stage.slug,
                'sequence': wr.current_stage.sequence,
                'color': wr.current_stage.color,
                'allows_edit': wr.current_stage.allows_edit,
                'requires_approval': wr.current_stage.requires_approval,
                'requires_signature': wr.current_stage.requires_signature,
            },
            'all_stages': all_stages,
            'valid_transitions': transitions,
            'approval_status': approval_status,
            'entered_stage_at': wr.entered_stage_at,
            'estimated_exit_date': wr.estimated_exit_date,
            'is_overdue': wr.is_overdue,
            'history': list(history),
        })

    @action(detail=True, methods=['post'], url_path='transition')
    def do_transition(self, request, pk=None):
        """
        Transition a workflow record to a new stage.
        Validates permissions, required fields, approval gates, and e-signatures.
        """
        workflow_record = self.get_object()
        serializer = TransitionActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ip_address = request.META.get('REMOTE_ADDR')

        try:
            updated_record = WorkflowService.transition(
                workflow_record=workflow_record,
                to_stage_slug=serializer.validated_data['to_stage_slug'],
                user=request.user,
                comments=serializer.validated_data.get('comments', ''),
                signature_password=serializer.validated_data.get('signature_password'),
                ip_address=ip_address,
            )
            return Response(
                WorkflowRecordDetailSerializer(updated_record).data,
                status=status.HTTP_200_OK
            )
        except TransitionNotAllowed as e:
            return Response({'error': str(e), 'code': 'transition_not_allowed'},
                            status=status.HTTP_400_BAD_REQUEST)
        except ApprovalRequired as e:
            return Response({'error': str(e), 'code': 'approval_required'},
                            status=status.HTTP_400_BAD_REQUEST)
        except FieldValidationError as e:
            return Response({'error': str(e), 'code': 'field_validation_error'},
                            status=status.HTTP_400_BAD_REQUEST)
        except SignatureRequired as e:
            return Response({'error': str(e), 'code': 'signature_required'},
                            status=status.HTTP_400_BAD_REQUEST)
        except WorkflowError as e:
            return Response({'error': str(e), 'code': 'workflow_error'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='valid-next-states')
    def valid_next_states(self, request, pk=None):
        """Return all valid next stages for this workflow record."""
        workflow_record = self.get_object()
        transitions = WorkflowService.get_valid_transitions(workflow_record)
        return Response(transitions)

    @action(detail=True, methods=['get'], url_path='approval-status')
    def approval_status(self, request, pk=None):
        """Check approval status for current stage."""
        workflow_record = self.get_object()
        status_data = WorkflowService.get_approval_status(workflow_record)
        return Response(status_data)

    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        """Get complete transition history for this record."""
        workflow_record = self.get_object()
        from .serializers import WorkflowHistorySerializer
        history = workflow_record.history.all().select_related(
            'from_stage', 'to_stage', 'transitioned_by'
        )
        return Response(WorkflowHistorySerializer(history, many=True).data)

    @action(detail=True, methods=['post'], url_path='add-approver')
    def add_approver(self, request, pk=None):
        """Add an approver to a gate in the current stage."""
        workflow_record = self.get_object()
        serializer = AddApproverSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            approver = User.objects.get(id=serializer.validated_data['approver_id'])
            req, created = WorkflowService.add_approver(
                workflow_record=workflow_record,
                gate_id=serializer.validated_data['gate_id'],
                approver_user=approver,
            )
            return Response(
                WorkflowApprovalRequestSerializer(req).data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except WorkflowError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='extend-deadline')
    def extend_deadline(self, request, pk=None):
        """Extend the SLA deadline for the current stage."""
        workflow_record = self.get_object()
        serializer = ExtendDeadlineSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ip_address = request.META.get('REMOTE_ADDR')
        WorkflowService.extend_deadline(
            workflow_record=workflow_record,
            days=serializer.validated_data['days'],
            reason=serializer.validated_data['reason'],
            user=request.user,
            ip_address=ip_address,
        )
        return Response(
            WorkflowRecordSerializer(workflow_record).data,
            status=status.HTTP_200_OK
        )


class WorkflowApprovalRequestViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View and respond to approval requests.
    """
    serializer_class = WorkflowApprovalRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = WorkflowApprovalRequest.objects.select_related(
            'gate', 'gate__stage', 'approver',
            'workflow_record', 'workflow_record__workflow',
        )
        # By default, show only current user's requests
        mine = self.request.query_params.get('mine', 'true')
        if mine == 'true':
            qs = qs.filter(approver=self.request.user)
        # Filter by status
        req_status = self.request.query_params.get('status')
        if req_status:
            qs = qs.filter(status=req_status)
        return qs

    @action(detail=True, methods=['post'], url_path='respond')
    def respond(self, request, pk=None):
        """Respond to an approval request (approve/reject)."""
        approval_request = self.get_object()
        serializer = ApprovalResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ip_address = request.META.get('REMOTE_ADDR')

        try:
            updated = WorkflowService.respond_to_approval(
                approval_request=approval_request,
                status=serializer.validated_data['status'],
                user=request.user,
                comments=serializer.validated_data.get('comments', ''),
                signature_password=serializer.validated_data.get('signature_password'),
                ip_address=ip_address,
            )
            return Response(
                WorkflowApprovalRequestSerializer(updated).data,
                status=status.HTTP_200_OK
            )
        except SignatureRequired as e:
            return Response({'error': str(e), 'code': 'signature_required'},
                            status=status.HTTP_400_BAD_REQUEST)
        except WorkflowError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PendingActionsViewSet(viewsets.ViewSet):
    """
    Dashboard endpoint: "Records Pending My Attention"
    Returns all pending approvals and overdue records for the current user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        # Pending approvals
        pending_approvals = WorkflowApprovalRequest.objects.filter(
            approver=request.user,
            status='pending',
        ).select_related(
            'gate', 'gate__stage', 'workflow_record',
            'workflow_record__workflow', 'workflow_record__current_stage',
        )

        # Records I own that are overdue
        # (This requires knowing ownership — module-specific, so we return pending approvals for now)

        return Response({
            'pending_approvals': WorkflowApprovalRequestSerializer(
                pending_approvals, many=True
            ).data,
            'pending_count': pending_approvals.count(),
        })


class WorkflowDelegationViewSet(viewsets.ModelViewSet):
    """Manage approval delegations."""
    serializer_class = WorkflowDelegationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WorkflowDelegation.objects.filter(
            delegator=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(delegator=self.request.user)
