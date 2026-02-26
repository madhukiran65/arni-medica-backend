from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, CharFilter, ChoiceFilter, BooleanFilter, DateFromToRangeFilter
from rest_framework.filters import SearchFilter
from django.db.models import Q, Count

from .models import Supplier, SupplierEvaluation
from .serializers import (
    SupplierListSerializer,
    SupplierDetailSerializer,
    SupplierCreateSerializer,
    SupplierEvaluationSerializer,
    SupplierDocumentSerializer,
    SupplierCorrectiveActionSerializer,
)


class SupplierFilterSet(FilterSet):
    """FilterSet for Supplier with advanced filtering."""
    name_or_code = CharFilter(
        method='filter_name_or_code',
        label='Name or Code'
    )
    search = CharFilter(
        method='filter_search',
        label='Search'
    )
    is_active = BooleanFilter(
        field_name='qualification_status',
        method='filter_is_active',
        label='Active'
    )
    requalification_due = DateFromToRangeFilter(
        field_name='next_evaluation_date',
        label='Requalification Date Range'
    )

    class Meta:
        model = Supplier
        fields = ['supplier_type', 'qualification_status', 'risk_level', 'country']

    def filter_name_or_code(self, queryset, name, value):
        """Filter by supplier name or code."""
        return queryset.filter(Q(name__icontains=value) | Q(supplier_id__icontains=value))

    def filter_search(self, queryset, name, value):
        """Search across name, code, and description."""
        return queryset.filter(
            Q(name__icontains=value) |
            Q(supplier_id__icontains=value) |
            Q(description__icontains=value)
        )

    def filter_is_active(self, queryset, name, value):
        """Filter by active/inactive status."""
        if value:
            return queryset.exclude(qualification_status__in=['suspended', 'disqualified'])
        else:
            return queryset.filter(qualification_status__in=['suspended', 'disqualified'])


class SupplierViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Suppliers.
    Supports filtering, searching, evaluations, documents, and corrective actions.
    """
    queryset = Supplier.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = SupplierFilterSet
    search_fields = ['supplier_id', 'name', 'contact_name', 'description']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SupplierDetailSerializer
        elif self.action == 'list':
            return SupplierListSerializer
        elif self.action == 'create':
            return SupplierCreateSerializer
        return SupplierDetailSerializer

    def perform_create(self, serializer):
        """Set created_by and updated_by to current user on creation."""
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        """Set updated_by to current user on update."""
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['get', 'post'])
    def evaluations(self, request, pk=None):
        """
        Get all evaluations for a supplier or create a new evaluation.
        """
        supplier = self.get_object()
        
        if request.method == 'GET':
            evaluations = supplier.evaluations.all()
            serializer = SupplierEvaluationSerializer(evaluations, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = SupplierEvaluationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(supplier=supplier)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'])
    def documents(self, request, pk=None):
        """
        Get all documents for a supplier or upload a new document.
        """
        supplier = self.get_object()
        
        if request.method == 'GET':
            documents = supplier.documents.all()
            serializer = SupplierDocumentSerializer(documents, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = SupplierDocumentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(supplier=supplier)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'])
    def corrective_actions(self, request, pk=None):
        """
        Get all corrective actions for a supplier or create a new corrective action.
        """
        supplier = self.get_object()
        
        if request.method == 'GET':
            corrective_actions = supplier.corrective_actions.all()
            serializer = SupplierCorrectiveActionSerializer(corrective_actions, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = SupplierCorrectiveActionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(supplier=supplier)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def supplier_stats(self, request):
        """
        Get supplier statistics: counts by status, type, risk_level, and avg qualification time.
        """
        from django.utils import timezone
        from datetime import timedelta

        total = self.queryset.count()
        by_status = self.queryset.values('qualification_status').annotate(count=Count('id'))
        by_type = self.queryset.values('supplier_type').annotate(count=Count('id'))
        by_risk = self.queryset.values('risk_level').annotate(count=Count('id'))

        # Calculate average time from creation to qualification
        qualified = self.queryset.filter(qualified_date__isnull=False)
        avg_qual_days = 0
        if qualified.exists():
            total_days = sum((q.qualified_date - q.created_at.date()).days for q in qualified)
            avg_qual_days = total_days // len(qualified) if qualified.count() > 0 else 0

        return Response({
            'total': total,
            'by_status': list(by_status),
            'by_type': list(by_type),
            'by_risk': list(by_risk),
            'avg_qualification_days': avg_qual_days,
        })

    @action(detail=False, methods=['get'])
    def pending_qualification(self, request):
        """
        Get suppliers pending qualification (pending_evaluation or pending_audit status).
        """
        pending = self.queryset.filter(
            qualification_status__in=['pending_evaluation', 'pending_audit']
        )
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def due_for_requalification(self, request):
        """
        Get suppliers past their requalification date.
        """
        from django.utils import timezone
        today = timezone.now().date()

        due = self.queryset.filter(
            next_evaluation_date__lt=today,
            qualification_status='qualified'
        )
        serializer = self.get_serializer(due, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def qualify(self, request, pk=None):
        """
        Transition supplier to qualified status with evaluation record.
        """
        from django.utils import timezone
        supplier = self.get_object()

        supplier.qualification_status = 'qualified'
        supplier.qualified_date = timezone.now().date()

        # Set next evaluation date (e.g., 1 year from now)
        if not supplier.next_evaluation_date:
            from datetime import timedelta
            supplier.next_evaluation_date = timezone.now().date() + timedelta(days=365)

        supplier.updated_by = request.user
        supplier.save()

        serializer = self.get_serializer(supplier)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """
        Suspend a supplier with reason.
        """
        supplier = self.get_object()
        reason = request.data.get('reason', '')

        supplier.qualification_status = 'suspended'
        supplier.qualification_notes = reason
        supplier.updated_by = request.user
        supplier.save()

        serializer = self.get_serializer(supplier)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def disqualify(self, request, pk=None):
        """
        Disqualify a supplier with reason.
        """
        supplier = self.get_object()
        reason = request.data.get('reason', '')

        supplier.qualification_status = 'disqualified'
        supplier.qualification_notes = reason
        supplier.updated_by = request.user
        supplier.save()

        serializer = self.get_serializer(supplier)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        """
        Get activity history/timeline for a supplier.
        """
        supplier = self.get_object()

        timeline_data = {
            'created': {
                'date': supplier.created_at,
                'action': 'Supplier Created',
                'user': supplier.created_by.username if supplier.created_by else 'System'
            },
            'qualified': None,
            'evaluations': [],
            'documents': [],
            'corrective_actions': []
        }

        if supplier.qualified_date:
            timeline_data['qualified'] = {
                'date': supplier.qualified_date,
                'action': 'Supplier Qualified'
            }

        for eval in supplier.evaluations.all():
            timeline_data['evaluations'].append({
                'date': eval.evaluation_date,
                'action': f'{eval.get_evaluation_type_display()} - {eval.get_recommendation_display()}',
                'score': float(eval.overall_score)
            })

        for doc in supplier.documents.all():
            timeline_data['documents'].append({
                'date': doc.uploaded_at,
                'action': f'Document: {doc.title}'
            })

        for ca in supplier.corrective_actions.all():
            timeline_data['corrective_actions'].append({
                'date': ca.created_at,
                'action': f'SCAR {ca.scar_number} - {ca.get_status_display()}'
            })

        return Response(timeline_data)

    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """
        List all documents for a supplier.
        """
        supplier = self.get_object()
        documents = supplier.documents.all()
        serializer = SupplierDocumentSerializer(documents, many=True, context={'request': request})
        return Response(serializer.data)


class SupplierEvaluationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Supplier Evaluations.
    Provides CRUD operations for supplier evaluations.
    """
    queryset = SupplierEvaluation.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SupplierEvaluationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['supplier', 'evaluation_type', 'recommendation']
    search_fields = ['supplier__name', 'comments']

    def perform_create(self, serializer):
        serializer.save(evaluator=self.request.user)

    def perform_update(self, serializer):
        serializer.save(evaluator=self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Complete an evaluation with score and result.
        """
        evaluation = self.get_object()

        # Update evaluation with data from request
        evaluation.overall_score = request.data.get('overall_score', evaluation.overall_score)
        evaluation.quality_score = request.data.get('quality_score', evaluation.quality_score)
        evaluation.delivery_score = request.data.get('delivery_score', evaluation.delivery_score)
        evaluation.service_score = request.data.get('service_score', evaluation.service_score)
        evaluation.compliance_score = request.data.get('compliance_score', evaluation.compliance_score)
        evaluation.recommendation = request.data.get('recommendation', evaluation.recommendation)
        evaluation.comments = request.data.get('comments', evaluation.comments)
        evaluation.save()

        serializer = self.get_serializer(evaluation)
        return Response(serializer.data, status=status.HTTP_200_OK)
