from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q, Avg
from .models import AIInsight
from .serializers import AIInsightSerializer, ModelStatusSerializer


class AIInsightViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AIInsight.objects.all()
    serializer_class = AIInsightSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def model_status(self, request):
        """Get status of AI models"""
        models = AIInsight.objects.values('model_used').annotate(
            insight_count=Count('id'),
            high_confidence_count=Count('id', filter=Q(confidence__gte=80)),
            acted_upon_count=Count('id', filter=Q(is_acted_upon=True)),
            accuracy_rate=Avg('confidence')
        ).order_by('-insight_count')

        data = []
        for model in models:
            data.append({
                'model_name': model['model_used'] or 'Unknown',
                'insight_count': model['insight_count'],
                'high_confidence_count': model['high_confidence_count'],
                'acted_upon_count': model['acted_upon_count'],
                'accuracy_rate': model['accuracy_rate'] or 0,
            })

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def mark_acted_upon(self, request, pk=None):
        """Mark insight as acted upon"""
        insight = self.get_object()
        insight.is_acted_upon = True
        insight.action_taken = request.data.get('action_taken', '')
        insight.save()
        
        return Response(
            AIInsightSerializer(insight).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Filter insights by type"""
        insight_type = request.query_params.get('type')
        if insight_type:
            insights = self.queryset.filter(insight_type=insight_type)
        else:
            insights = self.queryset

        serializer = self.get_serializer(insights, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def high_priority(self, request):
        """Get high priority insights (high severity or high confidence)"""
        insights = self.queryset.filter(
            Q(severity='high') | Q(confidence__gte=85)
        ).order_by('-confidence')

        serializer = self.get_serializer(insights, many=True)
        return Response(serializer.data)
