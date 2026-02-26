from rest_framework import viewsets, status, views, generics
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .models import AIInsight
from .serializers import AIInsightSerializer, ModelStatusSerializer
from .services import (
    QualityTrendAnalyzer,
    RiskAnalyzer,
    ComplianceMonitor,
    PredictiveAnalytics,
)
from .dashboard import ExecutiveDashboard

# Import models from other apps
from documents.models import Document
from capa.models import CAPA
from deviations.models import Deviation
from complaints.models import Complaint
from change_controls.models import ChangeControl
from suppliers.models import Supplier
from training.models import TrainingCourse, TrainingAssignment
from audit_mgmt.models import AuditPlan


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


class EnhancedDashboardView(views.APIView):
    """Enhanced Dashboard with comprehensive metrics and KPIs"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Get enhanced dashboard data"""
        # Summary counts
        total_documents = Document.objects.count()
        total_capas = CAPA.objects.count()
        total_deviations = Deviation.objects.count()
        total_complaints = Complaint.objects.count()
        total_change_controls = ChangeControl.objects.count()
        total_suppliers = Supplier.objects.count()
        total_training_courses = TrainingCourse.objects.count()
        total_audit_plans = AuditPlan.objects.count()

        # Calculate quality score (0-100)
        quality_score = self._calculate_quality_score()

        # Get overdue items
        now = timezone.now()
        overdue_documents = Document.objects.filter(
            next_review_date__lt=now
        ).count()

        overdue_capas = CAPA.objects.filter(
            current_phase__in=['investigation', 'root_cause', 'risk_affirmation', 'capa_plan'],
            target_completion_date__lt=now
        ).count()

        overdue_deviations = Deviation.objects.filter(
            current_stage__in=['opened', 'qa_review', 'investigation', 'capa_plan'],
            target_closure_date__lt=now
        ).count()

        overdue_training = TrainingAssignment.objects.filter(
            status='assigned',
            due_date__lt=now
        ).count()

        overdue_change_controls = ChangeControl.objects.filter(
            current_stage__in=['submitted', 'screening', 'impact_assessment', 'approval', 'implementation'],
            target_completion_date__lt=now
        ).count()

        # Get trends data (last 12 months)
        capas_by_month = self._get_capas_by_month(12)
        complaints_by_month = self._get_complaints_by_month(12)
        deviations_by_month = self._get_deviations_by_month(12)

        # Count pending actions
        pending_actions = (
            CAPA.objects.filter(current_phase__in=['investigation', 'root_cause']).count() +
            Deviation.objects.filter(current_stage__in=['opened', 'qa_review']).count() +
            ChangeControl.objects.filter(current_stage__in=['submitted', 'screening']).count()
        )

        # Calculate compliance rate
        compliance_rate = self._calculate_compliance_rate()

        # Calculate training compliance
        training_compliance = self._calculate_training_compliance()

        return Response({
            'summary': {
                'total_documents': total_documents,
                'total_capas': total_capas,
                'total_deviations': total_deviations,
                'total_complaints': total_complaints,
                'total_change_controls': total_change_controls,
                'total_suppliers': total_suppliers,
                'total_training_courses': total_training_courses,
                'total_audit_plans': total_audit_plans,
            },
            'quality_score': quality_score,
            'overdue_items': {
                'documents_overdue_review': overdue_documents,
                'capas_overdue': overdue_capas,
                'deviations_overdue': overdue_deviations,
                'training_overdue': overdue_training,
                'change_controls_overdue': overdue_change_controls,
            },
            'trends': {
                'capas_by_month': capas_by_month,
                'complaints_by_month': complaints_by_month,
                'deviations_by_month': deviations_by_month,
            },
            'pending_actions': pending_actions,
            'compliance_rate': compliance_rate,
            'training_compliance': training_compliance,
        }, status=status.HTTP_200_OK)

    def _calculate_quality_score(self):
        """Calculate overall quality score (0-100)"""
        try:
            return QualityTrendAnalyzer.get_quality_score().get('overall_score', 75)
        except:
            return 75

    def _get_capas_by_month(self, months=12):
        """Get CAPA data by month"""
        data = []
        now = timezone.now()
        for i in range(months, 0, -1):
            month_start = now - timedelta(days=30 * i)
            month_end = now - timedelta(days=30 * (i - 1))

            opened = CAPA.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()

            closed = CAPA.objects.filter(
                status='closed',
                updated_at__gte=month_start,
                updated_at__lt=month_end
            ).count()

            data.append({
                'month': month_start.strftime('%Y-%m'),
                'opened': opened,
                'closed': closed,
            })
        return data

    def _get_complaints_by_month(self, months=12):
        """Get complaint data by month"""
        data = []
        now = timezone.now()
        for i in range(months, 0, -1):
            month_start = now - timedelta(days=30 * i)
            month_end = now - timedelta(days=30 * (i - 1))

            count = Complaint.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()

            data.append({
                'month': month_start.strftime('%Y-%m'),
                'count': count,
            })
        return data

    def _get_deviations_by_month(self, months=12):
        """Get deviation data by month"""
        data = []
        now = timezone.now()
        for i in range(months, 0, -1):
            month_start = now - timedelta(days=30 * i)
            month_end = now - timedelta(days=30 * (i - 1))

            count = Deviation.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()

            data.append({
                'month': month_start.strftime('%Y-%m'),
                'count': count,
            })
        return data

    def _calculate_compliance_rate(self):
        """Calculate overall compliance rate (0-100)"""
        try:
            total_required = Document.objects.count()
            if total_required == 0:
                return 100
            reviewed = Document.objects.filter(
                last_reviewed_date__isnull=False
            ).count()
            return round((reviewed / total_required) * 100, 2)
        except:
            return 80

    def _calculate_training_compliance(self):
        """Calculate training compliance rate (0-100)"""
        try:
            total_courses = TrainingCourse.objects.count()
            if total_courses == 0:
                return 100
            completed = TrainingCourse.objects.filter(
                status='completed'
            ).count()
            return round((completed / total_courses) * 100, 2)
        except:
            return 75


class AIRecommendationsView(views.APIView):
    """AI-generated recommendations based on system analysis"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Get AI recommendations"""
        recommendations = []
        now = timezone.now()

        # Check for overdue CAPAs
        overdue_capas = CAPA.objects.filter(
            current_phase__in=['investigation', 'root_cause', 'risk_affirmation', 'capa_plan'],
            target_completion_date__lt=now
        ).count()
        if overdue_capas > 0:
            recommendations.append({
                'type': 'critical',
                'module': 'capa',
                'title': f'{overdue_capas} CAPAs are overdue',
                'description': f'{overdue_capas} CAPA(s) have passed their target completion date.',
                'action': 'Review and update target dates or escalate to management',
                'priority': 'high'
            })

        # Check for open deviations
        open_deviations = Deviation.objects.filter(
            current_stage__in=['opened', 'qa_review', 'investigation']
        ).count()
        if open_deviations > 3:
            recommendations.append({
                'type': 'warning',
                'module': 'deviations',
                'title': f'{open_deviations} active deviations under investigation',
                'description': f'Currently tracking {open_deviations} deviation(s) requiring investigation or closure.',
                'action': 'Review investigation progress and accelerate closure',
                'priority': 'high'
            })

        # Check for training compliance
        overdue_training = TrainingAssignment.objects.filter(
            status='assigned',
            due_date__lt=now
        ).count()
        if overdue_training > 0:
            recommendations.append({
                'type': 'warning',
                'module': 'training',
                'title': f'{overdue_training} training courses overdue',
                'description': f'{overdue_training} scheduled training course(s) have not been completed.',
                'action': 'Schedule immediate training sessions and track completion',
                'priority': 'high'
            })

        # Check for high-risk change controls
        high_risk_changes = ChangeControl.objects.filter(
            risk_level='high',
            current_stage__in=['submitted', 'screening', 'impact_assessment']
        ).count()
        if high_risk_changes > 0:
            recommendations.append({
                'type': 'critical',
                'module': 'change_controls',
                'title': f'{high_risk_changes} high-risk changes pending approval',
                'description': f'High-risk change control(s) are awaiting approval and require immediate review.',
                'action': 'Expedite risk assessment and approval process',
                'priority': 'critical'
            })

        # Check for documents needing review
        overdue_documents = Document.objects.filter(
            next_review_date__lt=now
        ).count()
        if overdue_documents > 0:
            recommendations.append({
                'type': 'warning',
                'module': 'documents',
                'title': f'{overdue_documents} documents pending review',
                'description': f'{overdue_documents} document(s) are overdue for their scheduled review.',
                'action': 'Schedule reviews and update document status',
                'priority': 'medium'
            })

        # Check for open complaints without CAPAs
        open_complaints = Complaint.objects.filter(
            status='open'
        ).count()
        if open_complaints > 2:
            recommendations.append({
                'type': 'info',
                'module': 'complaints',
                'title': f'{open_complaints} open complaints',
                'description': f'{open_complaints} complaint(s) are awaiting investigation or closure.',
                'action': 'Assess complaints and create CAPAs if necessary',
                'priority': 'medium'
            })

        # Check for pending change controls
        pending_changes = ChangeControl.objects.filter(
            current_stage__in=['submitted', 'screening']
        ).count()
        if pending_changes > 5:
            recommendations.append({
                'type': 'info',
                'module': 'change_controls',
                'title': f'{pending_changes} changes awaiting initial screening',
                'description': f'Backlog of {pending_changes} change control(s) in initial stages.',
                'action': 'Allocate resources to complete initial screening',
                'priority': 'medium'
            })

        # Success recommendation if all is well
        if len(recommendations) == 0:
            recommendations.append({
                'type': 'success',
                'module': 'system',
                'title': 'All systems operating normally',
                'description': 'No critical items requiring immediate attention.',
                'action': 'Continue routine monitoring and compliance activities',
                'priority': 'low'
            })

        return Response({
            'recommendations': recommendations
        }, status=status.HTTP_200_OK)


class QualityTrendsView(views.APIView):
    """Quality and compliance trends for dashboard charts"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Get trend data for charts"""
        # Get CAPA trends
        capa_data = self._get_capa_trends()

        # Get complaint trends
        complaint_data = self._get_complaint_trends()

        # Get deviation severity distribution
        deviation_severity = self._get_deviation_severity_distribution()

        return Response({
            'capa_trends': capa_data,
            'complaint_trends': complaint_data,
            'deviation_severity': deviation_severity,
        }, status=status.HTTP_200_OK)

    def _get_capa_trends(self):
        """Get CAPA trend data for the last 12 months"""
        data = []
        now = timezone.now()
        for i in range(12, 0, -1):
            month_start = now - timedelta(days=30 * i)
            month_end = now - timedelta(days=30 * (i - 1))

            opened = CAPA.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()

            closed = CAPA.objects.filter(
                status='closed',
                updated_at__gte=month_start,
                updated_at__lt=month_end
            ).count()

            data.append({
                'month': month_start.strftime('%b'),
                'opened': opened,
                'closed': closed,
            })
        return data

    def _get_complaint_trends(self):
        """Get complaint trend data for the last 12 months"""
        data = []
        now = timezone.now()
        for i in range(12, 0, -1):
            month_start = now - timedelta(days=30 * i)
            month_end = now - timedelta(days=30 * (i - 1))

            count = Complaint.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()

            data.append({
                'month': month_start.strftime('%b'),
                'count': count,
            })
        return data

    def _get_deviation_severity_distribution(self):
        """Get distribution of deviations by severity"""
        severities = ['critical', 'major', 'minor']
        data = []

        for severity in severities:
            count = Deviation.objects.filter(
                severity=severity
            ).count()
            data.append({
                'severity': severity,
                'count': count,
            })

        return data
