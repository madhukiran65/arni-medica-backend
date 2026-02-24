from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import CAPA, CAPAAction
from .serializers import CAPASerializer, CAPAActionSerializer, CAPATransitionSerializer


class CAPAViewSet(viewsets.ModelViewSet):
    queryset = CAPA.objects.all()
    serializer_class = CAPASerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        """Transition CAPA status following state machine"""
        capa = self.get_object()
        serializer = CAPATransitionSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                capa.transition_to(serializer.validated_data['new_status'])
                return Response(
                    {'status': 'success', 'new_status': capa.status},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def actions(self, request, pk=None):
        """Get all actions for a CAPA"""
        capa = self.get_object()
        actions = capa.actions.all()
        serializer = CAPAActionSerializer(actions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close CAPA with signature verification"""
        capa = self.get_object()
        serializer = CAPATransitionSerializer(data={'new_status': 'closed', **request.data})
        
        if serializer.is_valid():
            if 'signature' not in request.data:
                return Response(
                    {'error': 'Signature required to close CAPA'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                capa.transition_to('closed')
                capa.completed_date = request.data.get('completed_date')
                capa.save()
                return Response(
                    CAPASerializer(capa).data,
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CAPAActionViewSet(viewsets.ModelViewSet):
    queryset = CAPAAction.objects.all()
    serializer_class = CAPAActionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
