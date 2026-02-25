"""
Comprehensive AI insights services for quality management analytics.

Provides advanced analytics across CAPA, Complaints, Deviations, Training, and Documents
with trend analysis, risk assessment, compliance monitoring, and predictive capabilities.
"""

from django.db.models import Count, Avg, Q, F, Sum, Case, When, Value, IntegerField
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
import statistics
from collections import defaultdict

from capa.models import CAPA
from complaints.models import Complaint
from deviations.models import Deviation
from training.models import TrainingAssignment, TrainingComplianceRecord
from documents.models import Document


class QualityTrendAnalyzer:
    """Analyzes trends across CAPA, Complaints, and Deviations."""

    @staticmethod
    def get_capa_trends(days=90):
        """
        Returns CAPA metrics: open count, avg closure days, overdue count, by category, trend data.

        Args:
            days (int): Number of days to analyze (default 90)

        Returns:
            dict: Comprehensive CAPA metrics including trends, breakdowns, and SLAs
        """
        try:
            cutoff_date = timezone.now() - timedelta(days=days)

            # Query CAPA data
            all_capas = CAPA.objects.all()
            recent_capas = all_capas.filter(created_at__gte=cutoff_date)

            # Open and overdue counts
            open_capas = all_capas.filter(current_phase__in=[
                'investigation', 'root_cause', 'risk_affirmation',
                'capa_plan', 'implementation', 'effectiveness'
            ])
            closed_capas = all_capas.filter(current_phase='closure')

            # Calculate overdue CAPAs
            overdue_capas = open_capas.filter(
                target_completion_date__lt=timezone.now().date()
            ).exclude(target_completion_date__isnull=True)

            # Average days to close (for closed ones)
            closure_times = []
            for capa in closed_capas:
                if capa.closed_date and capa.created_at:
                    days_to_close = (capa.closed_date - capa.created_at).days
                    closure_times.append(days_to_close)

            avg_closure_days = statistics.mean(closure_times) if closure_times else 0

            # Breakdown by category
            category_breakdown = recent_capas.values('category').annotate(
                count=Count('id'),
                avg_days=Avg(Case(
                    When(closed_date__isnull=False),
                    then=(F('closed_date') - F('created_at'))
                ))
            ).order_by('-count')

            # Breakdown by priority
            priority_breakdown = recent_capas.values('priority').annotate(
                count=Count('id')
            ).order_by('-count')

            # Weekly trend data
            weekly_trends = []
            for week in range(weeks := (days // 7)):
                week_start = cutoff_date + timedelta(weeks=week)
                week_end = week_start + timedelta(weeks=1)
                week_data = recent_capas.filter(
                    created_at__gte=week_start,
                    created_at__lt=week_end
                )
                weekly_trends.append({
                    'week': week + 1,
                    'start_date': week_start.date(),
                    'created': week_data.count(),
                    'closed': week_data.filter(current_phase='closure').count(),
                })

            return {
                'total_count': all_capas.count(),
                'recent_count': recent_capas.count(),
                'open_count': open_capas.count(),
                'closed_count': closed_capas.count(),
                'overdue_count': overdue_capas.count(),
                'avg_closure_days': round(avg_closure_days, 2),
                'closure_rate_percent': round(
                    (closed_capas.count() / all_capas.count() * 100)
                    if all_capas.exists() else 0, 2
                ),
                'by_category': [
                    {
                        'category': item['category'] or 'Unknown',
                        'count': item['count'],
                        'avg_days': round(item['avg_days'] or 0, 2),
                    }
                    for item in category_breakdown
                ],
                'by_priority': [
                    {'priority': item['priority'], 'count': item['count']}
                    for item in priority_breakdown
                ],
                'weekly_trends': weekly_trends,
            }
        except Exception as e:
            return {
                'error': str(e),
                'open_count': 0,
                'closed_count': 0,
                'overdue_count': 0,
                'avg_closure_days': 0,
            }

    @staticmethod
    def get_complaint_trends(days=90):
        """
        Returns complaint metrics: open count, MDR reportable count, avg resolution days, by product.

        Args:
            days (int): Number of days to analyze

        Returns:
            dict: Comprehensive complaint metrics and trends
        """
        try:
            cutoff_date = timezone.now() - timedelta(days=days)

            all_complaints = Complaint.objects.all()
            recent_complaints = all_complaints.filter(received_date__gte=cutoff_date)

            # Status breakdown
            open_complaints = recent_complaints.exclude(status__in=['closed', 'rejected'])
            closed_complaints = recent_complaints.filter(status='closed')

            # Reportable complaints
            mdr_reportable = recent_complaints.filter(is_reportable_to_fda=True)
            mdr_submitted = recent_complaints.filter(mdr_submission_status='submitted')

            # Resolution time (for closed complaints)
            resolution_times = []
            for complaint in closed_complaints:
                if complaint.actual_closure_date and complaint.received_date:
                    days_to_resolve = (
                        complaint.actual_closure_date - complaint.received_date.date()
                    ).days
                    resolution_times.append(days_to_resolve)

            avg_resolution_days = statistics.mean(resolution_times) if resolution_times else 0

            # Breakdown by product
            product_breakdown = recent_complaints.values('product_name').annotate(
                count=Count('id'),
                mdr_count=Count('id', filter=Q(is_reportable_to_fda=True)),
                severity_critical=Count('id', filter=Q(severity='critical')),
                severity_major=Count('id', filter=Q(severity='major')),
            ).order_by('-count')[:10]

            # Breakdown by severity
            severity_breakdown = recent_complaints.values('severity').annotate(
                count=Count('id')
            ).order_by('-count')

            # Weekly trends
            weekly_trends = []
            for week in range(weeks := (days // 7)):
                week_start = cutoff_date + timedelta(weeks=week)
                week_end = week_start + timedelta(weeks=1)
                week_data = recent_complaints.filter(
                    received_date__gte=week_start,
                    received_date__lt=week_end
                )
                weekly_trends.append({
                    'week': week + 1,
                    'start_date': week_start.date(),
                    'received': week_data.count(),
                    'closed': week_data.filter(status='closed').count(),
                    'mdr_reportable': week_data.filter(is_reportable_to_fda=True).count(),
                })

            return {
                'total_count': all_complaints.count(),
                'recent_count': recent_complaints.count(),
                'open_count': open_complaints.count(),
                'closed_count': closed_complaints.count(),
                'mdr_reportable_count': mdr_reportable.count(),
                'mdr_reported_percent': round(
                    (mdr_submitted.count() / mdr_reportable.count() * 100)
                    if mdr_reportable.exists() else 0, 2
                ),
                'avg_resolution_days': round(avg_resolution_days, 2),
                'closure_rate_percent': round(
                    (closed_complaints.count() / recent_complaints.count() * 100)
                    if recent_complaints.exists() else 0, 2
                ),
                'by_product': [
                    {
                        'product_name': item['product_name'],
                        'count': item['count'],
                        'mdr_count': item['mdr_count'],
                        'severity_critical': item['severity_critical'],
                        'severity_major': item['severity_major'],
                    }
                    for item in product_breakdown
                ],
                'by_severity': [
                    {'severity': item['severity'], 'count': item['count']}
                    for item in severity_breakdown
                ],
                'weekly_trends': weekly_trends,
            }
        except Exception as e:
            return {
                'error': str(e),
                'open_count': 0,
                'closed_count': 0,
                'mdr_reportable_count': 0,
                'avg_resolution_days': 0,
            }

    @staticmethod
    def get_deviation_trends(days=90):
        """
        Returns deviation metrics: open count, by severity, by department, recurrence analysis.

        Args:
            days (int): Number of days to analyze

        Returns:
            dict: Comprehensive deviation metrics and trends
        """
        try:
            cutoff_date = timezone.now() - timedelta(days=days)

            all_deviations = Deviation.objects.all()
            recent_deviations = all_deviations.filter(reported_date__gte=cutoff_date)

            # Status breakdown
            open_deviations = recent_deviations.exclude(current_stage='completed')
            closed_deviations = recent_deviations.filter(current_stage='completed')

            # Severity breakdown
            severity_breakdown = recent_deviations.values('severity').annotate(
                count=Count('id')
            ).order_by('-count')

            # Closure time
            closure_times = []
            for deviation in closed_deviations:
                if deviation.actual_closure_date and deviation.reported_date:
                    days_to_close = (
                        deviation.actual_closure_date - deviation.reported_date
                    ).days
                    closure_times.append(days_to_close)

            avg_closure_days = statistics.mean(closure_times) if closure_times else 0

            # Breakdown by department
            department_breakdown = recent_deviations.values(
                'department__name'
            ).annotate(
                count=Count('id'),
                critical_count=Count('id', filter=Q(severity='critical')),
                major_count=Count('id', filter=Q(severity='major')),
            ).order_by('-count')

            # Breakdown by source
            source_breakdown = recent_deviations.values('source').annotate(
                count=Count('id')
            ).order_by('-count')

            # Recurrence analysis
            recurring_deviations = recent_deviations.filter(is_recurring=True)

            # Weekly trends
            weekly_trends = []
            for week in range(weeks := (days // 7)):
                week_start = cutoff_date + timedelta(weeks=week)
                week_end = week_start + timedelta(weeks=1)
                week_data = recent_deviations.filter(
                    reported_date__gte=week_start,
                    reported_date__lt=week_end
                )
                weekly_trends.append({
                    'week': week + 1,
                    'start_date': week_start.date(),
                    'reported': week_data.count(),
                    'closed': week_data.filter(current_stage='completed').count(),
                })

            return {
                'total_count': all_deviations.count(),
                'recent_count': recent_deviations.count(),
                'open_count': open_deviations.count(),
                'closed_count': closed_deviations.count(),
                'recurring_count': recurring_deviations.count(),
                'avg_closure_days': round(avg_closure_days, 2),
                'closure_rate_percent': round(
                    (closed_deviations.count() / recent_deviations.count() * 100)
                    if recent_deviations.exists() else 0, 2
                ),
                'by_severity': [
                    {'severity': item['severity'], 'count': item['count']}
                    for item in severity_breakdown
                ],
                'by_department': [
                    {
                        'department': item['department__name'] or 'Unknown',
                        'count': item['count'],
                        'critical': item['critical_count'],
                        'major': item['major_count'],
                    }
                    for item in department_breakdown
                ],
                'by_source': [
                    {'source': item['source'], 'count': item['count']}
                    for item in source_breakdown
                ],
                'weekly_trends': weekly_trends,
            }
        except Exception as e:
            return {
                'error': str(e),
                'open_count': 0,
                'closed_count': 0,
                'recurring_count': 0,
                'avg_closure_days': 0,
            }

    @staticmethod
    def get_quality_score():
        """
        Calculates an overall quality health score 0-100.

        Weighting:
        - CAPA on-time closure (25%)
        - Complaint resolution (25%)
        - Deviation rate (20%)
        - Training compliance (15%)
        - Document currency (15%)

        Returns:
            dict: Quality score with breakdown and recommendations
        """
        try:
            scores = {}

            # 1. CAPA On-Time Closure (25%)
            try:
                all_capas = CAPA.objects.filter(current_phase='closure')
                if all_capas.exists():
                    on_time = all_capas.filter(
                        closed_date__lte=F('target_completion_date')
                    ).exclude(target_completion_date__isnull=True).count()
                    capa_score = (on_time / all_capas.count() * 100) if all_capas.exists() else 0
                    scores['capa_on_time'] = min(capa_score, 100)
                else:
                    scores['capa_on_time'] = 100  # No closed CAPAs = assume compliant
            except:
                scores['capa_on_time'] = 50

            # 2. Complaint Resolution (25%)
            try:
                all_complaints = Complaint.objects.filter(status='closed')
                if all_complaints.exists():
                    resolved = all_complaints.filter(
                        actual_closure_date__lte=F('target_closure_date')
                    ).exclude(target_closure_date__isnull=True).count()
                    complaint_score = (resolved / all_complaints.count() * 100) if all_complaints.exists() else 0
                    scores['complaint_resolution'] = min(complaint_score, 100)
                else:
                    scores['complaint_resolution'] = 100
            except:
                scores['complaint_resolution'] = 50

            # 3. Deviation Rate (20%) - lower is better
            try:
                recent_deviations = Deviation.objects.filter(
                    reported_date__gte=timezone.now() - timedelta(days=90)
                ).count()
                # Assume 50 deviations in 90 days is poor (20 score), 0 is excellent
                deviation_score = max(100 - (recent_deviations / 50 * 100), 0)
                scores['deviation_rate'] = min(deviation_score, 100)
            except:
                scores['deviation_rate'] = 50

            # 4. Training Compliance (15%)
            try:
                all_assignments = TrainingAssignment.objects.all()
                if all_assignments.exists():
                    completed = all_assignments.filter(
                        status__in=['completed', 'waived']
                    ).count()
                    training_score = (completed / all_assignments.count() * 100)
                    scores['training_compliance'] = min(training_score, 100)
                else:
                    scores['training_compliance'] = 100
            except:
                scores['training_compliance'] = 50

            # 5. Document Currency (15%)
            try:
                released_docs = Document.objects.filter(vault_state='released')
                if released_docs.exists():
                    current = released_docs.filter(
                        next_review_date__gte=timezone.now().date()
                    ).count()
                    doc_score = (current / released_docs.count() * 100)
                    scores['document_currency'] = min(doc_score, 100)
                else:
                    scores['document_currency'] = 100
            except:
                scores['document_currency'] = 50

            # Calculate weighted score
            weights = {
                'capa_on_time': 0.25,
                'complaint_resolution': 0.25,
                'deviation_rate': 0.20,
                'training_compliance': 0.15,
                'document_currency': 0.15,
            }

            overall_score = sum(
                scores.get(key, 50) * weight
                for key, weight in weights.items()
            )

            # Generate recommendations
            recommendations = []
            if scores.get('capa_on_time', 100) < 80:
                recommendations.append('Improve CAPA closure rate - review blocked items')
            if scores.get('complaint_resolution', 100) < 80:
                recommendations.append('Accelerate complaint resolution - identify bottlenecks')
            if scores.get('deviation_rate', 100) < 70:
                recommendations.append('High deviation frequency - implement preventive measures')
            if scores.get('training_compliance', 100) < 85:
                recommendations.append('Increase training compliance rates')
            if scores.get('document_currency', 100) < 90:
                recommendations.append('Update overdue documents')

            if not recommendations:
                recommendations.append('Quality metrics are strong - maintain current practices')

            return {
                'overall_score': round(overall_score, 1),
                'breakdown': {key: round(value, 1) for key, value in scores.items()},
                'recommendations': recommendations,
                'rating': 'Excellent' if overall_score >= 85 else (
                    'Good' if overall_score >= 75 else (
                        'Fair' if overall_score >= 60 else 'Poor'
                    )
                ),
            }
        except Exception as e:
            return {
                'error': str(e),
                'overall_score': 0,
                'breakdown': {},
                'recommendations': ['Unable to calculate quality score'],
            }


class RiskAnalyzer:
    """Risk matrix and trending analysis."""

    @staticmethod
    def get_risk_matrix_summary():
        """
        Returns current risk distribution across all CAPAs.

        Returns:
            dict: Risk matrix heatmap data organized by severity and occurrence
        """
        try:
            # Initialize 5x5 matrix
            matrix = defaultdict(lambda: defaultdict(int))

            capas = CAPA.objects.all()

            for capa in capas:
                severity = capa.risk_severity
                occurrence = capa.risk_occurrence
                rpn = capa.risk_priority_number

                matrix[severity][occurrence] += 1

            # Convert to list format for heatmap
            heatmap_data = []
            for severity in range(1, 6):
                row = []
                for occurrence in range(1, 6):
                    count = matrix[severity][occurrence]
                    rpn = severity * occurrence
                    row.append({
                        'severity': severity,
                        'occurrence': occurrence,
                        'count': count,
                        'rpn': rpn,
                        'risk_level': 'High' if rpn > 15 else (
                            'Medium' if rpn > 5 else 'Low'
                        ),
                    })
                heatmap_data.append(row)

            # Risk statistics
            all_rpns = [capa.risk_priority_number for capa in capas]
            high_risk = sum(1 for capa in capas if capa.risk_priority_number > 15)
            medium_risk = sum(1 for capa in capas if 5 < capa.risk_priority_number <= 15)
            low_risk = sum(1 for capa in capas if capa.risk_priority_number <= 5)

            return {
                'matrix': heatmap_data,
                'statistics': {
                    'total_capas': capas.count(),
                    'high_risk_count': high_risk,
                    'medium_risk_count': medium_risk,
                    'low_risk_count': low_risk,
                    'avg_rpn': round(statistics.mean(all_rpns), 1) if all_rpns else 0,
                    'max_rpn': max(all_rpns) if all_rpns else 0,
                },
            }
        except Exception as e:
            return {
                'error': str(e),
                'matrix': [],
                'statistics': {},
            }

    @staticmethod
    def identify_high_risk_areas():
        """
        Identifies areas with concentrated risk.

        Returns:
            dict: Risk areas with scores and severity counts
        """
        try:
            high_risk_areas = {}

            # Risk by CAPA category
            category_risks = CAPA.objects.exclude(
                current_phase='closure'
            ).values('category').annotate(
                count=Count('id'),
                avg_rpn=Avg(
                    Case(
                        When(risk_severity__gte=1),
                        then=F('risk_severity') * F('risk_occurrence')
                    )
                ),
                high_severity_count=Count('id', filter=Q(risk_severity__gte=4)),
            ).order_by('-avg_rpn')

            # Risk by department
            dept_risks = CAPA.objects.exclude(
                current_phase='closure'
            ).values('department__name').annotate(
                count=Count('id'),
                avg_rpn=Avg(
                    Case(
                        When(risk_severity__gte=1),
                        then=F('risk_severity') * F('risk_occurrence')
                    )
                ),
            ).order_by('-avg_rpn')

            # Risk by complaint product
            product_risks = Complaint.objects.filter(
                is_reportable_to_fda=True
            ).values('product_name').annotate(
                count=Count('id'),
                critical_count=Count('id', filter=Q(severity='critical')),
            ).order_by('-count')[:5]

            # Risk by deviation department
            deviation_risks = Deviation.objects.filter(
                is_recurring=True
            ).values('department__name').annotate(
                count=Count('id'),
                critical_count=Count('id', filter=Q(severity='critical')),
            ).order_by('-count')[:5]

            return {
                'by_capa_category': [
                    {
                        'category': item['category'] or 'Unknown',
                        'open_count': item['count'],
                        'avg_rpn': round(item['avg_rpn'] or 0, 1),
                        'high_severity_count': item['high_severity_count'],
                        'risk_score': min(round(item['avg_rpn'] or 0, 1), 100),
                    }
                    for item in category_risks
                ],
                'by_department': [
                    {
                        'department': item['department__name'] or 'Unknown',
                        'count': item['count'],
                        'avg_rpn': round(item['avg_rpn'] or 0, 1),
                        'risk_score': min(round(item['avg_rpn'] or 0, 1), 100),
                    }
                    for item in dept_risks
                ],
                'reportable_complaints': [
                    {
                        'product': item['product_name'],
                        'count': item['count'],
                        'critical': item['critical_count'],
                    }
                    for item in product_risks
                ],
                'recurring_deviations': [
                    {
                        'department': item['department__name'] or 'Unknown',
                        'count': item['count'],
                        'critical': item['critical_count'],
                    }
                    for item in deviation_risks
                ],
            }
        except Exception as e:
            return {
                'error': str(e),
                'by_capa_category': [],
                'by_department': [],
            }


class ComplianceMonitor:
    """Monitors compliance status across all modules."""

    @staticmethod
    def get_training_compliance():
        """
        Returns training compliance percentage by department/job function.

        Returns:
            dict: Compliance metrics by department and overall
        """
        try:
            # Overall training compliance
            all_assignments = TrainingAssignment.objects.all()
            completed = all_assignments.filter(
                status__in=['completed', 'waived']
            ).count()
            overdue = all_assignments.filter(
                status='overdue',
                due_date__lt=timezone.now()
            ).count()

            overall_compliance = (
                (completed / all_assignments.count() * 100)
                if all_assignments.exists() else 100
            )

            # By department
            dept_compliance = TrainingComplianceRecord.objects.values(
                'department__name'
            ).annotate(
                avg_compliance=Avg('compliance_percentage'),
                total_overdue=Sum('total_overdue'),
                total_completed=Sum('total_completed'),
            ).order_by('-avg_compliance')

            return {
                'overall_compliance_percent': round(overall_compliance, 1),
                'total_required': all_assignments.count(),
                'total_completed': completed,
                'total_overdue': overdue,
                'by_department': [
                    {
                        'department': item['department__name'] or 'Unknown',
                        'compliance_percent': round(item['avg_compliance'] or 0, 1),
                        'completed': item['total_completed'] or 0,
                        'overdue': item['total_overdue'] or 0,
                    }
                    for item in dept_compliance
                ],
                'rating': 'Excellent' if overall_compliance >= 90 else (
                    'Good' if overall_compliance >= 75 else (
                        'Fair' if overall_compliance >= 60 else 'Poor'
                    )
                ),
            }
        except Exception as e:
            return {
                'error': str(e),
                'overall_compliance_percent': 0,
                'total_required': 0,
                'total_completed': 0,
            }

    @staticmethod
    def get_document_compliance():
        """
        Returns document review compliance.

        Returns:
            dict: Document status and review metrics
        """
        try:
            all_docs = Document.objects.all()
            released_docs = all_docs.filter(vault_state='released')

            # Documents past review date
            past_review = released_docs.filter(
                next_review_date__lt=timezone.now().date()
            ).exclude(next_review_date__isnull=True)

            # Documents in draft/review too long (> 30 days)
            thirty_days_ago = timezone.now() - timedelta(days=30)
            stuck_in_review = all_docs.filter(
                vault_state__in=['draft'],
                created_at__lt=thirty_days_ago
            )

            # Compliance calculation
            on_schedule = released_docs.filter(
                next_review_date__gte=timezone.now().date()
            ).exclude(next_review_date__isnull=True).count()

            compliance_percent = (
                (on_schedule / released_docs.count() * 100)
                if released_docs.exists() else 100
            )

            # By type
            by_type = Document.objects.values(
                'infocard_type__name'
            ).annotate(
                total=Count('id'),
                past_review=Count('id', filter=Q(
                    vault_state='released',
                    next_review_date__lt=timezone.now().date()
                )),
            ).order_by('-past_review')

            return {
                'total_documents': all_docs.count(),
                'released_documents': released_docs.count(),
                'compliance_percent': round(compliance_percent, 1),
                'past_review_count': past_review.count(),
                'stuck_in_draft': stuck_in_review.count(),
                'by_document_type': [
                    {
                        'type': item['infocard_type__name'],
                        'total': item['total'],
                        'past_review': item['past_review'],
                    }
                    for item in by_type
                ],
                'rating': 'Good' if compliance_percent >= 80 else (
                    'Fair' if compliance_percent >= 60 else 'Poor'
                ),
            }
        except Exception as e:
            return {
                'error': str(e),
                'total_documents': 0,
                'compliance_percent': 0,
            }

    @staticmethod
    def get_audit_readiness_score():
        """
        Returns overall audit readiness score.

        Returns:
            dict: Audit readiness assessment with action items
        """
        try:
            scores = {}
            issues = []

            # 1. CAPA Closure
            open_capas = CAPA.objects.exclude(current_phase='closure')
            if open_capas.filter(target_completion_date__lt=timezone.now().date()).exists():
                scores['capa_closure'] = 60
                issues.append(f"{open_capas.filter(target_completion_date__lt=timezone.now().date()).count()} overdue CAPAs")
            else:
                scores['capa_closure'] = 100

            # 2. Complaint Resolution
            open_complaints = Complaint.objects.exclude(status__in=['closed', 'rejected'])
            if open_complaints.count() > 10:
                scores['complaint_resolution'] = max(100 - (open_complaints.count() - 10) * 5, 50)
                issues.append(f"{open_complaints.count()} open complaints")
            else:
                scores['complaint_resolution'] = 100

            # 3. Deviation Management
            open_deviations = Deviation.objects.exclude(current_stage='completed')
            if open_deviations.count() > 5:
                scores['deviation_management'] = max(100 - (open_deviations.count() - 5) * 8, 50)
                issues.append(f"{open_deviations.count()} open deviations")
            else:
                scores['deviation_management'] = 100

            # 4. Training Compliance
            training_compliance = ComplianceMonitor.get_training_compliance()
            training_percent = training_compliance.get('overall_compliance_percent', 0)
            scores['training_compliance'] = training_percent
            if training_percent < 85:
                issues.append(f"Training compliance at {training_percent}%")

            # 5. Document Currency
            doc_compliance = ComplianceMonitor.get_document_compliance()
            doc_percent = doc_compliance.get('compliance_percent', 0)
            scores['document_control'] = doc_percent
            if doc_percent < 85:
                issues.append(f"Document compliance at {doc_percent}%")

            # Calculate audit readiness
            avg_score = sum(scores.values()) / len(scores) if scores else 0

            return {
                'audit_readiness_score': round(avg_score, 1),
                'breakdown': {key: round(value, 1) for key, value in scores.items()},
                'issues': issues[:5] if issues else ['No critical issues identified'],
                'rating': 'Audit Ready' if avg_score >= 85 else (
                    'Minor Gaps' if avg_score >= 70 else 'Significant Gaps'
                ),
            }
        except Exception as e:
            return {
                'error': str(e),
                'audit_readiness_score': 0,
                'breakdown': {},
                'issues': [],
            }


class PredictiveAnalytics:
    """Simple predictive analytics using statistical methods."""

    @staticmethod
    def predict_capa_volume(months_ahead=3):
        """
        Uses simple linear regression to predict future CAPA volume.

        Args:
            months_ahead (int): Number of months to predict (default 3)

        Returns:
            dict: CAPA volume predictions
        """
        try:
            # Get last 12 months of CAPA creation data
            month_data = []
            for i in range(12, 0, -1):
                start = timezone.now() - timedelta(days=30*i)
                end = timezone.now() - timedelta(days=30*(i-1))
                count = CAPA.objects.filter(
                    created_at__gte=start,
                    created_at__lt=end
                ).count()
                month_data.append(count)

            if len(month_data) < 2:
                return {
                    'error': 'Insufficient historical data',
                    'predictions': [],
                }

            # Simple linear regression
            x = list(range(len(month_data)))
            y = month_data

            mean_x = sum(x) / len(x)
            mean_y = sum(y) / len(y)

            numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x)))
            denominator = sum((x[i] - mean_x) ** 2 for i in range(len(x)))

            if denominator == 0:
                slope = 0
            else:
                slope = numerator / denominator

            intercept = mean_y - slope * mean_x

            # Generate predictions
            predictions = []
            for month in range(1, months_ahead + 1):
                x_pred = len(month_data) + month - 1
                y_pred = slope * x_pred + intercept
                predictions.append({
                    'month_ahead': month,
                    'predicted_volume': max(0, round(y_pred, 0)),
                    'confidence': 'Medium' if len(month_data) >= 6 else 'Low',
                })

            # Trend analysis
            trend = 'Increasing' if slope > 0.5 else (
                'Decreasing' if slope < -0.5 else 'Stable'
            )

            return {
                'historical_avg': round(sum(y) / len(y), 1),
                'trend': trend,
                'slope': round(slope, 2),
                'predictions': predictions,
            }
        except Exception as e:
            return {
                'error': str(e),
                'predictions': [],
            }

    @staticmethod
    def identify_recurring_issues():
        """
        Finds patterns in recurring quality issues.

        Returns:
            dict: Recurring issue patterns and clusters
        """
        try:
            # Recurring CAPAs
            recurring_capas = CAPA.objects.filter(is_recurring=True)

            # Group by category
            category_patterns = recurring_capas.values('category').annotate(
                count=Count('id'),
                avg_recurrence=Avg('recurrence_count')
            ).order_by('-count')

            # Group by source
            source_patterns = recurring_capas.values('source').annotate(
                count=Count('id')
            ).order_by('-count')

            # Department concentration
            dept_patterns = recurring_capas.values('department__name').annotate(
                count=Count('id')
            ).order_by('-count')[:5]

            # Recurring deviations
            recurring_devs = Deviation.objects.filter(is_recurring=True)

            # Product trends (from complaints)
            trending_complaints = Complaint.objects.filter(
                is_trending=True
            ).values('product_name').annotate(
                count=Count('id')
            ).order_by('-count')[:5]

            return {
                'recurring_capa_count': recurring_capas.count(),
                'by_category': [
                    {
                        'category': item['category'] or 'Unknown',
                        'count': item['count'],
                        'avg_recurrences': round(item['avg_recurrence'] or 0, 1),
                    }
                    for item in category_patterns
                ],
                'by_source': [
                    {'source': item['source'], 'count': item['count']}
                    for item in source_patterns
                ],
                'by_department': [
                    {
                        'department': item['department__name'] or 'Unknown',
                        'count': item['count'],
                    }
                    for item in dept_patterns
                ],
                'recurring_deviations': recurring_devs.count(),
                'trending_products': [
                    {
                        'product': item['product_name'],
                        'trend_count': item['count'],
                    }
                    for item in trending_complaints
                ],
            }
        except Exception as e:
            return {
                'error': str(e),
                'recurring_capa_count': 0,
                'by_category': [],
            }
