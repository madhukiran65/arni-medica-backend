from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .models import Supplier, SupplierEvaluation
from .serializers import (
    SupplierListSerializer,
    SupplierDetailSerializer,
    SupplierCreateSerializer,
    SupplierEvaluationSerializer,
    SupplierDocumentSerializer,
    SupplierCorrectiveActionSerializer,
)


class SupplierViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Suppliers.
    Supports filtering, searching, evaluations, documents, and corrective actions.
    """
    queryset = Supplier.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['supplier_type', 'qualification_status', 'risk_level']
    search_fields = ['supplier_id', 'name', 'contact_name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SupplierDetailSerializer
        elif self.action == 'list':
            return SupplierListSerializer
        elif self.action == 'create':
            return SupplierCreateSerializer
        return SupplierDetailSerializer

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

    @action(detail=True, methods=['post'])
    def qualify(self, request, pk=None):
        """
        Change supplier status to qualified.
        """
        supplier = self.get_object()
        supplier.qualification_status = 'qualified'
        supplier.save()
        
        serializer = self.get_serializer(supplier)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """
        Suspend a supplier.
        """
        supplier = self.get_object()
        supplier.qualification_status = 'suspended'
        supplier.save()
        
        serializer = self.get_serializer(supplier)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SupplierEvaluationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Supplier Evaluations.
    Provides CRUD operations for supplier evaluations.
    """
    queryset = SupplierEvaluation.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SupplierEvaluationSerializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()
