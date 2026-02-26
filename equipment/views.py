from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from equipment.models import (
    Equipment,
    EquipmentQualification,
    CalibrationSchedule,
    CalibrationRecord,
    MaintenanceSchedule,
    MaintenanceRecord,
    EquipmentDocument,
)
from equipment.serializers import (
    EquipmentListSerializer,
    EquipmentDetailSerializer,
    EquipmentQualificationListSerializer,
    EquipmentQualificationDetailSerializer,
    CalibrationScheduleSerializer,
    CalibrationRecordListSerializer,
    CalibrationRecordDetailSerializer,
    MaintenanceScheduleSerializer,
    MaintenanceRecordListSerializer,
    MaintenanceRecordDetailSerializer,
    EquipmentDocumentListSerializer,
    EquipmentDocumentDetailSerializer,
)
from equipment.filters import (
    EquipmentFilter,
    EquipmentQualificationFilter,
    CalibrationScheduleFilter,
    CalibrationRecordFilter,
    MaintenanceScheduleFilter,
    MaintenanceRecordFilter,
    EquipmentDocumentFilter,
)


class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EquipmentFilter
    search_fields = ['equipment_id', 'name', 'serial_number', 'manufacturer']
    ordering_fields = ['equipment_id', 'name', 'status', 'criticality', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EquipmentDetailSerializer
        return EquipmentListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['patch'])
    def change_status(self, request, pk=None):
        equipment = self.get_object()
        new_status = request.data.get('status')

        if new_status not in dict(Equipment.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        equipment.status = new_status
        equipment.updated_by = request.user
        equipment.save()

        return Response(EquipmentDetailSerializer(equipment).data)

    @action(detail=True, methods=['get'])
    def calibration_status(self, request, pk=None):
        equipment = self.get_object()
        try:
            cal_schedule = equipment.calibration_schedule
            is_overdue = cal_schedule.is_overdue()
            days_until_due = cal_schedule.days_until_due()
        except CalibrationSchedule.DoesNotExist:
            is_overdue = None
            days_until_due = None

        return Response({
            'requires_calibration': equipment.requires_calibration,
            'is_overdue': is_overdue,
            'days_until_due': days_until_due,
        })

    @action(detail=True, methods=['get'])
    def maintenance_status(self, request, pk=None):
        equipment = self.get_object()
        schedules = equipment.maintenance_schedules.all()

        overdue_count = sum(1 for s in schedules if s.is_overdue())

        return Response({
            'requires_maintenance': equipment.requires_maintenance,
            'total_schedules': schedules.count(),
            'overdue_count': overdue_count,
        })


class EquipmentQualificationViewSet(viewsets.ModelViewSet):
    queryset = EquipmentQualification.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EquipmentQualificationFilter
    search_fields = ['qualification_id', 'equipment__name', 'protocol_number']
    ordering_fields = ['qualification_id', 'execution_date', 'status', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EquipmentQualificationDetailSerializer
        return EquipmentQualificationListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['patch'])
    def mark_approved(self, request, pk=None):
        qualification = self.get_object()
        qualification.approved_by = request.user
        qualification.status = 'completed'
        qualification.updated_by = request.user
        qualification.save()

        return Response(EquipmentQualificationDetailSerializer(qualification).data)


class CalibrationScheduleViewSet(viewsets.ModelViewSet):
    queryset = CalibrationSchedule.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = CalibrationScheduleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CalibrationScheduleFilter
    search_fields = ['equipment__name', 'equipment__equipment_id']
    ordering_fields = ['next_due', 'equipment__name', 'created_at']
    ordering = ['next_due']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['patch'])
    def update_calibration_date(self, request, pk=None):
        schedule = self.get_object()
        last_calibrated = request.data.get('last_calibrated')

        if not last_calibrated:
            return Response({'error': 'last_calibrated is required'}, status=status.HTTP_400_BAD_REQUEST)

        from datetime import timedelta, datetime
        schedule.last_calibrated = last_calibrated
        schedule.next_due = (datetime.strptime(last_calibrated, '%Y-%m-%d').date() +
                            timedelta(days=schedule.interval_days))
        schedule.updated_by = request.user
        schedule.save()

        return Response(CalibrationScheduleSerializer(schedule).data)

    @action(detail=True, methods=['get'])
    def overdue_equipment(self, request, pk=None):
        overdue_schedules = CalibrationSchedule.objects.filter(
            next_due__lt=filters.timezone.now().date()
        )
        serializer = CalibrationScheduleSerializer(overdue_schedules, many=True)
        return Response(serializer.data)


class CalibrationRecordViewSet(viewsets.ModelViewSet):
    queryset = CalibrationRecord.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CalibrationRecordFilter
    search_fields = ['calibration_id', 'equipment__name', 'certificate_number']
    ordering_fields = ['calibration_id', 'calibration_date', 'result', 'created_at']
    ordering = ['-calibration_date']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CalibrationRecordDetailSerializer
        return CalibrationRecordListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['patch'])
    def approve_record(self, request, pk=None):
        record = self.get_object()
        record.approved_by = request.user
        record.updated_by = request.user
        record.save()

        return Response(CalibrationRecordDetailSerializer(record).data)

    @action(detail=False, methods=['get'])
    def failed_records(self, request):
        failed_records = CalibrationRecord.objects.filter(result__in=['fail', 'out_of_tolerance'])
        serializer = CalibrationRecordListSerializer(failed_records, many=True)
        return Response(serializer.data)


class MaintenanceScheduleViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceSchedule.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = MaintenanceScheduleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MaintenanceScheduleFilter
    search_fields = ['equipment__name', 'equipment__equipment_id']
    ordering_fields = ['next_due', 'equipment__name', 'created_at']
    ordering = ['next_due']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['patch'])
    def update_maintenance_date(self, request, pk=None):
        schedule = self.get_object()
        last_performed = request.data.get('last_performed')

        if not last_performed:
            return Response({'error': 'last_performed is required'}, status=status.HTTP_400_BAD_REQUEST)

        from datetime import timedelta, datetime
        schedule.last_performed = last_performed
        schedule.next_due = (datetime.strptime(last_performed, '%Y-%m-%d').date() +
                            timedelta(days=schedule.interval_days))
        schedule.updated_by = request.user
        schedule.save()

        return Response(MaintenanceScheduleSerializer(schedule).data)


class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRecord.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MaintenanceRecordFilter
    search_fields = ['maintenance_id', 'equipment__name', 'description']
    ordering_fields = ['maintenance_id', 'maintenance_date', 'status', 'created_at']
    ordering = ['-maintenance_date']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MaintenanceRecordDetailSerializer
        return MaintenanceRecordListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['patch'])
    def complete_record(self, request, pk=None):
        record = self.get_object()
        record.status = 'completed'
        record.updated_by = request.user
        record.save()

        return Response(MaintenanceRecordDetailSerializer(record).data)

    @action(detail=False, methods=['get'])
    def pending_maintenance(self, request):
        pending = MaintenanceRecord.objects.filter(
            status__in=['scheduled', 'in_progress']
        ).order_by('maintenance_date')
        serializer = MaintenanceRecordListSerializer(pending, many=True)
        return Response(serializer.data)


class EquipmentDocumentViewSet(viewsets.ModelViewSet):
    queryset = EquipmentDocument.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EquipmentDocumentFilter
    search_fields = ['title', 'equipment__name', 'equipment__equipment_id']
    ordering_fields = ['title', 'document_type', 'expiry_date', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EquipmentDocumentDetailSerializer
        return EquipmentDocumentListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, uploaded_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=False, methods=['get'])
    def expiring_documents(self, request):
        from django.utils import timezone
        from datetime import timedelta

        expiring_soon = EquipmentDocument.objects.filter(
            expiry_date__gte=timezone.now().date(),
            expiry_date__lte=timezone.now().date() + timedelta(days=30)
        ).order_by('expiry_date')

        serializer = EquipmentDocumentListSerializer(expiring_soon, many=True)
        return Response(serializer.data)
