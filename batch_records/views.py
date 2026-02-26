from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import (
    MasterBatchRecord,
    BatchRecord,
    BatchStep,
    BatchDeviation,
    BatchMaterial,
    BatchEquipment,
)
from .serializers import (
    MasterBatchRecordListSerializer,
    MasterBatchRecordDetailSerializer,
    MasterBatchRecordApproveSerializer,
    MasterBatchRecordSupersedSerializer,
    MasterBatchRecordObsoleteSerializer,
    BatchRecordListSerializer,
    BatchRecordDetailSerializer,
    BatchRecordStartSerializer,
    BatchRecordCompleteSerializer,
    BatchRecordReleaseSerializer,
    BatchRecordRejectSerializer,
    BatchRecordQuarantineSerializer,
    BatchStepListSerializer,
    BatchStepDetailSerializer,
    BatchStepStartSerializer,
    BatchStepCompleteSerializer,
    BatchStepVerifySerializer,
    BatchStepSkipSerializer,
    BatchDeviationListSerializer,
    BatchDeviationDetailSerializer,
    BatchDeviationResolveSerializer,
    BatchDeviationCloseSerializer,
    BatchMaterialListSerializer,
    BatchMaterialDetailSerializer,
    BatchMaterialDispenseSerializer,
    BatchMaterialVerifySerializer,
    BatchMaterialConsumeSerializer,
    BatchEquipmentListSerializer,
    BatchEquipmentDetailSerializer,
    BatchEquipmentStartUsageSerializer,
    BatchEquipmentEndUsageSerializer,
    BatchEquipmentVerifyCalibrationSerializer,
    BatchEquipmentVerifyCleaningSerializer,
)


# ============================================================================
# FILTERS
# ============================================================================

class MasterBatchRecordFilter(django_filters.FilterSet):
    """Filter set for MasterBatchRecord."""
    created_at = django_filters.DateFromToRangeFilter()
    approval_date = django_filters.DateFromToRangeFilter()

    class Meta:
        model = MasterBatchRecord
        fields = {
            'mbr_id': ['icontains'],
            'product_code': ['icontains'],
            'status': ['exact'],
            'product_line': ['exact'],
        }


class BatchRecordFilter(django_filters.FilterSet):
    """Filter set for BatchRecord."""
    created_at = django_filters.DateFromToRangeFilter()
    started_at = django_filters.DateFromToRangeFilter()
    completed_at = django_filters.DateFromToRangeFilter()
    release_date = django_filters.DateFromToRangeFilter()

    class Meta:
        model = BatchRecord
        fields = {
            'batch_id': ['icontains'],
            'batch_number': ['icontains'],
            'lot_number': ['icontains'],
            'mbr': ['exact'],
            'status': ['exact'],
            'site': ['exact'],
            'has_deviations': ['exact'],
            'review_by_exception': ['exact'],
        }


class BatchStepFilter(django_filters.FilterSet):
    """Filter set for BatchStep."""
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = BatchStep
        fields = {
            'batch': ['exact'],
            'status': ['exact'],
            'requires_verification': ['exact'],
            'is_within_spec': ['exact'],
        }


class BatchDeviationFilter(django_filters.FilterSet):
    """Filter set for BatchDeviation."""
    created_at = django_filters.DateFromToRangeFilter()
    resolution_date = django_filters.DateFromToRangeFilter()

    class Meta:
        model = BatchDeviation
        fields = {
            'deviation_id': ['icontains'],
            'batch': ['exact'],
            'deviation_type': ['exact'],
            'status': ['exact'],
        }


class BatchMaterialFilter(django_filters.FilterSet):
    """Filter set for BatchMaterial."""
    class Meta:
        model = BatchMaterial
        fields = {
            'batch': ['exact'],
            'material_code': ['icontains'],
            'status': ['exact'],
        }


class BatchEquipmentFilter(django_filters.FilterSet):
    """Filter set for BatchEquipment."""
    class Meta:
        model = BatchEquipment
        fields = {
            'batch': ['exact'],
            'equipment': ['exact'],
        }


# ============================================================================
# VIEWSETS
# ============================================================================

class MasterBatchRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for MasterBatchRecord.

    list: Get all master batch records
    create: Create a new master batch record
    retrieve: Get details of a specific master batch record
    update: Update a master batch record
    partial_update: Partially update a master batch record
    destroy: Delete a master batch record
    approve: Approve a master batch record
    supersede: Mark as superseded
    obsolete: Mark as obsolete
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_class = MasterBatchRecordFilter
    search_fields = ['mbr_id', 'title', 'product_name', 'product_code']
    ordering_fields = ['created_at', 'updated_at', 'approval_date']
    ordering = ['-created_at']

    def get_queryset(self):
        return MasterBatchRecord.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MasterBatchRecordDetailSerializer
        return MasterBatchRecordListSerializer

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a master batch record."""
        mbr = self.get_object()
        serializer = MasterBatchRecordApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            mbr.approve(request.user)
            return Response(
                MasterBatchRecordDetailSerializer(mbr).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def supersede(self, request, pk=None):
        """Mark a master batch record as superseded."""
        mbr = self.get_object()
        serializer = MasterBatchRecordSupersedSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            mbr.supersede()
            return Response(
                MasterBatchRecordDetailSerializer(mbr).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def obsolete(self, request, pk=None):
        """Mark a master batch record as obsolete."""
        mbr = self.get_object()
        serializer = MasterBatchRecordObsoleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            mbr.obsolete()
            return Response(
                MasterBatchRecordDetailSerializer(mbr).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class BatchRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for BatchRecord.

    list: Get all batch records
    create: Create a new batch record
    retrieve: Get details of a specific batch record
    update: Update a batch record
    partial_update: Partially update a batch record
    destroy: Delete a batch record
    start: Start batch production
    complete: Complete batch production
    submit_for_review: Submit for review
    release: Release batch
    reject: Reject batch
    quarantine: Quarantine batch
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_class = BatchRecordFilter
    search_fields = ['batch_id', 'batch_number', 'lot_number']
    ordering_fields = ['created_at', 'started_at', 'completed_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return BatchRecord.objects.prefetch_related(
            'steps',
            'deviations',
            'materials',
            'equipment_usage'
        )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BatchRecordDetailSerializer
        return BatchRecordListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start batch production."""
        batch = self.get_object()
        serializer = BatchRecordStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            batch.start_production()
            return Response(
                BatchRecordDetailSerializer(batch).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete batch production."""
        batch = self.get_object()
        serializer = BatchRecordCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            batch.complete_production(
                quantity_produced=serializer.validated_data['quantity_produced'],
                quantity_rejected=serializer.validated_data.get(
                    'quantity_rejected',
                    0
                )
            )
            return Response(
                BatchRecordDetailSerializer(batch).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def submit_for_review(self, request, pk=None):
        """Submit batch for review."""
        batch = self.get_object()
        try:
            batch.submit_for_review()
            return Response(
                BatchRecordDetailSerializer(batch).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def release(self, request, pk=None):
        """Release batch."""
        batch = self.get_object()
        serializer = BatchRecordReleaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            batch.release(request.user)
            return Response(
                BatchRecordDetailSerializer(batch).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject batch."""
        batch = self.get_object()
        serializer = BatchRecordRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            batch.reject()
            return Response(
                BatchRecordDetailSerializer(batch).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def quarantine(self, request, pk=None):
        """Quarantine batch."""
        batch = self.get_object()
        serializer = BatchRecordQuarantineSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            batch.quarantine()
            return Response(
                BatchRecordDetailSerializer(batch).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class BatchStepViewSet(viewsets.ModelViewSet):
    """
    ViewSet for BatchStep.

    list: Get all batch steps
    create: Create a new batch step
    retrieve: Get details of a specific batch step
    update: Update a batch step
    partial_update: Partially update a batch step
    destroy: Delete a batch step
    start: Start step execution
    complete: Complete step with data
    verify: Verify completed step
    skip: Skip step
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]
    filterset_class = BatchStepFilter
    ordering_fields = ['batch', 'step_number', 'created_at']
    ordering = ['batch', 'step_number']

    def get_queryset(self):
        return BatchStep.objects.select_related('batch', 'operator', 'verifier')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BatchStepDetailSerializer
        return BatchStepListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start executing the batch step."""
        step = self.get_object()
        serializer = BatchStepStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            step.start_step(request.user)
            return Response(
                BatchStepDetailSerializer(step).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete batch step with actual values."""
        step = self.get_object()
        serializer = BatchStepCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            step.complete_step(serializer.validated_data['actual_values'])
            return Response(
                BatchStepDetailSerializer(step).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify completed batch step."""
        step = self.get_object()
        serializer = BatchStepVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            step.verify_step(request.user)
            return Response(
                BatchStepDetailSerializer(step).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def skip(self, request, pk=None):
        """Skip the batch step."""
        step = self.get_object()
        serializer = BatchStepSkipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            step.skip_step()
            return Response(
                BatchStepDetailSerializer(step).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class BatchDeviationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for BatchDeviation.

    list: Get all batch deviations
    create: Create a new batch deviation
    retrieve: Get details of a specific deviation
    update: Update a deviation
    partial_update: Partially update a deviation
    destroy: Delete a deviation
    resolve: Resolve a deviation
    close: Close a resolved deviation
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_class = BatchDeviationFilter
    search_fields = ['deviation_id', 'description']
    ordering_fields = ['created_at', 'resolution_date']
    ordering = ['-created_at']

    def get_queryset(self):
        return BatchDeviation.objects.select_related(
            'batch',
            'batch_step',
            'resolved_by'
        )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BatchDeviationDetailSerializer
        return BatchDeviationListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve a batch deviation."""
        deviation = self.get_object()
        serializer = BatchDeviationResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            if 'root_cause' in serializer.validated_data:
                deviation.root_cause = serializer.validated_data['root_cause']
            if 'immediate_action' in serializer.validated_data:
                deviation.immediate_action = (
                    serializer.validated_data['immediate_action']
                )
            deviation.save()
            deviation.resolve(request.user)
            return Response(
                BatchDeviationDetailSerializer(deviation).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close a resolved batch deviation."""
        deviation = self.get_object()
        serializer = BatchDeviationCloseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            deviation.close()
            return Response(
                BatchDeviationDetailSerializer(deviation).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class BatchMaterialViewSet(viewsets.ModelViewSet):
    """
    ViewSet for BatchMaterial.

    list: Get all batch materials
    create: Create a new batch material
    retrieve: Get details of a specific material
    update: Update a material
    partial_update: Partially update a material
    destroy: Delete a material
    dispense: Mark material as dispensed
    verify: Verify dispensed material
    consume: Mark material as consumed
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_class = BatchMaterialFilter
    search_fields = ['material_code', 'material_name', 'lot_number']
    ordering_fields = ['batch', 'material_code', 'created_at']
    ordering = ['batch', 'material_code']

    def get_queryset(self):
        return BatchMaterial.objects.select_related(
            'batch',
            'dispensed_by',
            'verified_by'
        )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BatchMaterialDetailSerializer
        return BatchMaterialListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def dispense(self, request, pk=None):
        """Dispense batch material."""
        material = self.get_object()
        serializer = BatchMaterialDispenseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            material.dispense(request.user)
            return Response(
                BatchMaterialDetailSerializer(material).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify dispensed material."""
        material = self.get_object()
        serializer = BatchMaterialVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            material.verify(request.user)
            return Response(
                BatchMaterialDetailSerializer(material).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def consume(self, request, pk=None):
        """Consume batch material."""
        material = self.get_object()
        serializer = BatchMaterialConsumeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            material.consume(serializer.validated_data['quantity_used'])
            return Response(
                BatchMaterialDetailSerializer(material).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class BatchEquipmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for BatchEquipment.

    list: Get all batch equipment
    create: Create a new batch equipment
    retrieve: Get details of specific equipment
    update: Update equipment
    partial_update: Partially update equipment
    destroy: Delete equipment
    start_usage: Start equipment usage
    end_usage: End equipment usage
    verify_calibration: Verify calibration
    verify_cleaning: Verify cleaning
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]
    filterset_class = BatchEquipmentFilter
    ordering_fields = ['batch', 'equipment_name', 'created_at']
    ordering = ['batch', 'equipment_name']

    def get_queryset(self):
        return BatchEquipment.objects.select_related(
            'batch',
            'equipment',
            'verified_by'
        )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BatchEquipmentDetailSerializer
        return BatchEquipmentListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def start_usage(self, request, pk=None):
        """Start equipment usage."""
        equipment = self.get_object()
        serializer = BatchEquipmentStartUsageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            equipment.start_usage()
            return Response(
                BatchEquipmentDetailSerializer(equipment).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def end_usage(self, request, pk=None):
        """End equipment usage."""
        equipment = self.get_object()
        serializer = BatchEquipmentEndUsageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            equipment.end_usage()
            return Response(
                BatchEquipmentDetailSerializer(equipment).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def verify_calibration(self, request, pk=None):
        """Verify equipment calibration."""
        equipment = self.get_object()
        serializer = BatchEquipmentVerifyCalibrationSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        try:
            equipment.verify_calibration(request.user)
            return Response(
                BatchEquipmentDetailSerializer(equipment).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def verify_cleaning(self, request, pk=None):
        """Verify equipment cleaning."""
        equipment = self.get_object()
        serializer = BatchEquipmentVerifyCleaningSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            equipment.verify_cleaning(request.user)
            return Response(
                BatchEquipmentDetailSerializer(equipment).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
