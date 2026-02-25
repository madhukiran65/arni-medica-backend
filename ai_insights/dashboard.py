"""
Executive Dashboard aggregation service.

Provides comprehensive dashboard data combining all analytics services
for executive-level insights and KPI tracking.
"""

from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from capa.models import CAPA
from complaints.models import Complaint
from deviations.models import Deviation
from training.models import TrainingAssignment
from documents.models import Document
from .services import (
    QualityTrendAnalyzer,
    RiskAnalyzer,
    ComplianceMonitor,
    PredictiveAnalytics,
)


class ExecutiveDashboard:
    """Aggregates all metrics for executive dashboard API."""

    @staticmethod
    def get_full_dashboard():
        """
        Returns complete dashboard data.

        Returns:
            dict: Complete dashboard with all metrics and analytics
        """
        try:
            dashboard_data = {}

            # Quality Score
            dashboard_data['quality_score'] = QualityTrendAnalyzer.get_quality_score()

            # Trend Summaries (90 days)
            dashboard_data['capa_summary'] = QualityTrendAnalyzer.get_capa_trends(90)
            dashboard_data['complaint_summary'] = QualityTrendAnalyzer.get_complaint_trends(90)
            dashboard_data['deviation_summary'] = QualityTrendAnalyzer.get_deviation_trends(90)

            # Risk Analysis
            dashboard_data['risk_matrix'] = RiskAnalyzer.get_risk_matrix_summary()
            dashboard_data['high_risk_areas'] = RiskAnalyzer.identify_high_risk_areas()

            # Compliance Status
            dashboard_data['training_compliance'] = ComplianceMonitor.get_training_compliance()
            dashboard_data['document_compliance'] = ComplianceMonitor.get_document_compliance()
            dashboard_data['audit_readiness'] = ComplianceMonitor.get_audit_readiness_score()

            # Predictions
            dashboard_data['capa_volume_forecast'] = PredictiveAnalytics.predict_capa_volume(3)
            dashboard_data['recurring_issues'] = PredictiveAnalytics.identify_recurring_issues()

            # Recent Activity (last 10 items across all modules)
            dashboard_data['recent_activity'] = ExecutiveDashboard._get_recent_activity()

            # Summary Cards
            dashboard_data['summary_cards'] = ExecutiveDashboard._get_summary_cards()

            return dashboard_data
        except Exception as e:
            return {
                'error': str(e),
                'quality_score': {'overall_score': 0},
                'summary_cards': {},
            }

    @staticmethod
    def get_kpi_summary():
        """
        Key Performance Indicators.

        Returns:
            dict: KPI summary with key metrics
        """
        try:
            kpis = {}

            # CAPA Closure Rate
            all_capas = CAPA.objects.filter(current_phase='closure')
            if all_capas.exists():
                on_time = all_capas.filter(
                    closed_date__lte=F('target_completion_date')
                ).exclude(target_completion_date__isnull=True).count()
                kpis['capa_closure_rate_percent'] = round(
                    (on_time / all_capas.count() * 100), 1
                )
            else:
                kpis['capa_closure_rate_percent'] = 100

            # Mean Time to Resolve Complaints
            closed_complaints = Complaint.objects.filter(status='closed')
            if closed_complaints.exists():
                total_time = 0
                count = 0
                for c in closed_complaints:
                    if c.actual_closure_date and c.received_date:
                        total_time += (c.actual_closure_date - c.received_date.date()).days
                        count += 1
                kpis['avg_complaint_resolution_days'] = round(
                    total_time / count, 1
                ) if count > 0 else 0
            else:
                kpis['avg_complaint_resolution_days'] = 0

            # Training Compliance
            all_assignments = TrainingAssignment.objects.all()
            if all_assignments.exists():
                completed = all_assignments.filter(
                    status__in=['completed', 'waived']
                ).count()
                kpis['training_compliance_percent'] = round(
                    (completed / all_assignments.count() * 100), 1
                )
            else:
                kpis['training_compliance_percent'] = 100

            # Document Review On-Time
            released_docs = Document.objects.filter(vault_state='released')
            if released_docs.exists():
                on_schedule = released_docs.filter(
                    next_review_date__gte=timezone.now().date()
                ).exclude(next_review_date__isnull=True).count()
                kpis['document_review_ontime_percent'] = round(
                    (on_schedule / released_docs.count() * 100), 1
                )
            else:
                kpis['document_review_ontime_percent'] = 100

            # Deviation Recurrence Rate
            all_deviations = Deviation.objects.all()
            if all_deviations.exists():
                recurring = all_deviations.filter(is_recurring=True).count()
                kpis['deviation_recurrence_rate_percent'] = round(
                    (recurring / all_deviations.count() * 100), 1
                )
            else:
                kpis['deviation_recurrence_rate_percent'] = 0

            # Complaint MDR Reporting Rate
            reportable = Complaint.objects.filter(is_reportable_to_fda=True)
            reported = Complaint.objects.filter(mdr_submission_status='submitted')
            if reportable.exists():
                kpis['mdr_reporting_rate_percent'] = round(
                    (reported.count() / reportable.count() * 100), 1
                )
            else:
                kpis['mdr_reporting_rate_percent'] = 100

            return kpis
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def _get_recent_activity():
        """
        Get last 10 items across all modules.

        Returns:
            list: Recent activity items with type and timestamp
        """
        try:
            activities = []

            # Recent CAPAs
            for capa in CAPA.objects.all().order_by('-created_at')[:3]:
                activities.append({
                    'type': 'CAPA',
                    'id': capa.capa_id,
                    'title': capa.title,
                    'status': capa.current_phase,
                    'timestamp': capa.created_at,
                })

            # Recent Complaints
            for complaint in Complaint.objects.all().order_by('-received_date')[:3]:
                activities.append({
                    'type': 'Complaint',
                    'id': complaint.complaint_id,
                    'title': f"{complaint.product_name} - {complaint.category}",
                    'status': complaint.status,
                    'timestamp': complaint.received_date,
                })

            # Recent Deviations
            for deviation in Deviation.objects.all().order_by('-reported_date')[:2]:
                activities.append({
                    'type': 'Deviation',
                    'id': deviation.deviation_id,
                    'title': deviation.title,
                    'status': deviation.current_stage,
                    'timestamp': deviation.reported_date,
                })

            # Recent Documents
            for doc in Document.objects.filter(
                vault_state='released'
            ).order_by('-released_date')[:2]:
                activities.append({
                    'type': 'Document',
                    'id': doc.document_id,
                    'title': doc.title,
                    'status': doc.vault_state,
                    'timestamp': doc.released_date or doc.created_at,
                })

            # Sort by timestamp and return last 10
            activities.sort(key=lambda x: x['timestamp'], reverse=True)
            return activities[:10]
        except Exception as e:
            return []

    @staticmethod
    def _get_summary_cards():
        """
        Get summary cards for dashboard overview.

        Returns:
            dict: Summary card data with counts and metrics
        """
        try:
            return {
                'open_capas': {
                    'count': CAPA.objects.exclude(current_phase='closure').count(),
                    'label': 'Open CAPAs',
                    'color': 'blue',
                },
                'overdue_capas': {
                    'count': CAPA.objects.exclude(
                        current_phase='closure'
                    ).filter(
                        target_completion_date__lt=timezone.now().date()
                    ).exclude(target_completion_date__isnull=True).count(),
                    'label': 'Overdue CAPAs',
                    'color': 'red',
                },
                'open_complaints': {
                    'count': Complaint.objects.exclude(
                        status__in=['closed', 'rejected']
                    ).count(),
                    'label': 'Open Complaints',
                    'color': 'orange',
                },
                'mdr_reportable': {
                    'count': Complaint.objects.filter(
                        is_reportable_to_fda=True
                    ).count(),
                    'label': 'MDR Reportable',
                    'color': 'red',
                },
                'open_deviations': {
                    'count': Deviation.objects.exclude(
                        current_stage='completed'
                    ).count(),
                    'label': 'Open Deviations',
                    'color': 'yellow',
                },
                'recurring_deviations': {
                    'count': Deviation.objects.filter(
                        is_recurring=True
                    ).count(),
                    'label': 'Recurring Deviations',
                    'color': 'purple',
                },
                'training_overdue': {
                    'count': TrainingAssignment.objects.filter(
                        status='overdue',
                        due_date__lt=timezone.now()
                    ).count(),
                    'label': 'Training Overdue',
                    'color': 'orange',
                },
                'document_past_review': {
                    'count': Document.objects.filter(
                        vault_state='released',
                        next_review_date__lt=timezone.now().date()
                    ).exclude(next_review_date__isnull=True).count(),
                    'label': 'Documents Past Review',
                    'color': 'orange',
                },
            }
        except Exception as e:
            return {}


# Import F for query expressions
from django.db.models import F
