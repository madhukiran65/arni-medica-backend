from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Complaint, ComplaintInvestigation
from .serializers import (
    ComplaintSerializer, ComplaintInvestigationSerializer,
    ComplaintInvestigateSerializer, ComplaintCreateCAPASerializer,
    ComplaintCloseSerializer
)


class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def investigate(self, request, pk=None):
        """Create investigation record for complaint"""
        complaint = self.get_object()
        serializer = ComplaintInvestigateSerializer(data=request.data)
        
        if serializer.is_valid():
            investigation = ComplaintInvestigation.objects.create(
                complaint=complaint,
                investigator=request.user,
                investigation_step=serializer.validated_data['investigation_step'],
                findings=serializer.validated_data['findings'],
                created_by=request.user,
                updated_by=request.user
            )
            complaint.status = 'under_investigation'
            complaint.save()
            
            return Response(
                ComplaintInvestigationSerializer(investigation).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def create_capa(self, request, pk=None):
        """Create CAPA from complaint"""
        complaint = self.get_object()
        serializer = ComplaintCreateCAPASerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                from capa.models import CAPA
                
                capa = CAPA.objects.create(
                    capa_id=f"CAPA-{complaint.complaint_id}",
                    title=serializer.validated_data['capa_title'],
                    source='complaint',
                    priority=serializer.validated_data['priority'],
                    owner=request.user,
                    description=serializer.validated_data['description'],
                    created_by=request.user,
                    updated_by=request.user
                )
                complaint.related_capa = capa
                complaint.status = 'capa_initiated'
                complaint.save()
                
                return Response(
                    {'success': True, 'capa_id': capa.id, 'capa_number': capa.capa_id},
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close complaint"""
        complaint = self.get_object()
        serializer = ComplaintCloseSerializer(data=request.data)
        
        if serializer.is_valid():
            complaint.investigation_summary = serializer.validated_data['investigation_summary']
            complaint.root_cause = serializer.validated_data.get('root_cause', '')
            complaint.impact_assessment = serializer.validated_data.get('impact_assessment', '')
            complaint.status = 'closed'
            complaint.updated_by = request.user
            complaint.save()
            
            return Response(
                ComplaintSerializer(complaint).data,
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ComplaintInvestigationViewSet(viewsets.ModelViewSet):
    queryset = ComplaintInvestigation.objects.all()
    serializer_class = ComplaintInvestigationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
