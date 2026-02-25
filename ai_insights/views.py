from rest_framework import viewsets, status, views, generics
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q, Avg
from .models import AIInsight
from .serializers import AIInsightSerializer, ModelStatusSerializer
from .services import (
    QualityTrendAnalyzer,
    RiskAnalyzer,
    ComplianceMonitor,
    PredictiveAnalytics,
)
from .dashboard import ExecutiveDashboard


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


class DashboardView(views.APIView):
    """Executive Dashboard endpoint"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Get full dashboard data"""
        dashboard_data = ExecutiveDashboard.get_full_dashboard()
        return Response(dashboard_data, status=status.HTTP_200_OK)


class KPIView(views.APIView):
    """Key Performance Indicators endpoint"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Get KPI summary"""
        kpis = ExecutiveDashboard.get_kpi_summary()
        return Response(kpis, status=status.HTTP_200_OK)


class CAPATrendsView(views.APIView):
    """CAPA Trends endpoint"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Get CAPA trends with optional days parameter"""
        days = int(request.query_params.get('days', 90))
        trends = QualityTrendAnalyzer.get_capa_trends(days)
        return Response(trends, status=status.HTTP_200_OK)


class ComplaintTrendsView(views.APIView):
    """Complaint Trends endpoint"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Get complaint trends with optional days parameter"""
        days = int(request.query_params.get('days', 90))
        trends = QualityTrendAnalyzer.get_complaint_trends(days)
        return Response(trends, status=status.HTTP_200_OK)


class DeviationTrendsView(views.APIView):
    """Deviation Trends endpoint"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Get deviation trends with optional days parameter"""
        days = int(request.query_params.get('days', 90))
        trends = QualityTrendAnalyzer.get_deviation_trends(days)
        return Response(trends, status=status.HTTP_200_OK)


class RiskMatrixView(views.APIView):
    """Risk Matrix endpoint"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Get risk matrix summary"""
        risk_matrix = RiskAnalyzer.get_risk_matrix_summary()
        return Response(risk_matrix, status=status.HTTP_200_OK)


class QualityScoreView(views.APIView):
    """Quality Score endpoint"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Get overall quality score"""
        score = QualityTrendAnalyzer.get_quality_score()
        return Response(score, status=status.HTTP_200_OK)


class ComplianceView(views.APIView):
    """Compliance Monitoring endpoint"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Get comprehensive compliance metrics"""
        compliance_type = request.query_params.get('type', 'all')

        data = {}

        if compliance_type in ['training', 'all']:
            data['training_compliance'] = ComplianceMonitor.get_training_compliance()

        if compliance_type in ['document', 'all']:
            data['document_compliance'] = ComplianceMonitor.get_document_compliance()

        if compliance_type in ['audit', 'all']:
            data['audit_readiness'] = ComplianceMonitor.get_audit_readiness_score()

        return Response(data, status=status.HTTP_200_OK)


class PredictionsView(views.APIView):
    """Predictive Analytics endpoint"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Get predictions and forecasts"""
        months = int(request.query_params.get('months', 3))

        data = {
            'capa_volume_forecast': PredictiveAnalytics.predict_capa_volume(months),
            'recurring_issues': PredictiveAnalytics.identify_recurring_issues(),
            'high_risk_areas': RiskAnalyzer.identify_high_risk_areas(),
        }

        return Response(data, status=status.HTTP_200_OK)
