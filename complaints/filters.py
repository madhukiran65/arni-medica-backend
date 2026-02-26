from django_filters import rest_framework as filters

from .models import (
    Complaint,
    PMSPlan,
    TrendAnalysis,
    PMSReport,
    VigilanceReport,
    LiteratureReview,
    SafetySignal,
)


class ComplaintFilterSet(filters.FilterSet):
    """FilterSet for Complaint"""

    status = filters.MultipleChoiceFilter(
        choices=Complaint.STATUS_CHOICES,
    )
    severity = filters.MultipleChoiceFilter(
        choices=Complaint.SEVERITY_CHOICES,
    )
    priority = filters.MultipleChoiceFilter(
        choices=Complaint.PRIORITY_CHOICES,
    )
    event_type = filters.MultipleChoiceFilter(
        choices=Complaint.EVENT_TYPE_CHOICES,
    )
    category = filters.MultipleChoiceFilter(
        choices=Complaint.CATEGORY_CHOICES,
    )
    department = filters.NumberFilter(field_name='department__id')
    assigned_to = filters.NumberFilter(field_name='assigned_to__id')
    is_reportable_to_fda = filters.BooleanFilter()
    mdr_submission_status = filters.MultipleChoiceFilter(
        choices=Complaint.MDR_SUBMISSION_STATUS_CHOICES,
    )
    received_date_after = filters.DateFilter(
        field_name='received_date',
        lookup_expr='gte',
    )
    received_date_before = filters.DateFilter(
        field_name='received_date',
        lookup_expr='lte',
    )

    class Meta:
        model = Complaint
        fields = [
            'status',
            'severity',
            'priority',
            'event_type',
            'category',
            'department',
            'assigned_to',
            'is_reportable_to_fda',
            'mdr_submission_status',
        ]


class PMSPlanFilterSet(filters.FilterSet):
    """FilterSet for PMSPlan"""

    status = filters.MultipleChoiceFilter(
        choices=PMSPlan.STATUS_CHOICES,
    )
    review_frequency = filters.MultipleChoiceFilter(
        choices=PMSPlan.REVIEW_FREQUENCY_CHOICES,
    )
    product_line = filters.NumberFilter(field_name='product_line__id')
    department = filters.NumberFilter(field_name='department__id')
    responsible_person = filters.NumberFilter(field_name='responsible_person__id')
    effective_date_after = filters.DateFilter(
        field_name='effective_date',
        lookup_expr='gte',
    )
    effective_date_before = filters.DateFilter(
        field_name='effective_date',
        lookup_expr='lte',
    )

    class Meta:
        model = PMSPlan
        fields = [
            'status',
            'review_frequency',
            'product_line',
            'department',
            'responsible_person',
        ]


class TrendAnalysisFilterSet(filters.FilterSet):
    """FilterSet for TrendAnalysis"""

    status = filters.MultipleChoiceFilter(
        choices=TrendAnalysis.STATUS_CHOICES,
    )
    trend_direction = filters.MultipleChoiceFilter(
        choices=TrendAnalysis.TREND_DIRECTION_CHOICES,
    )
    statistical_method = filters.MultipleChoiceFilter(
        choices=TrendAnalysis.STATISTICAL_METHOD_CHOICES,
    )
    pms_plan = filters.NumberFilter(field_name='pms_plan__id')
    product_line = filters.NumberFilter(field_name='product_line__id')
    analyzed_by = filters.NumberFilter(field_name='analyzed_by__id')
    threshold_breached = filters.BooleanFilter()
    analysis_period_start_after = filters.DateFilter(
        field_name='analysis_period_start',
        lookup_expr='gte',
    )
    analysis_period_start_before = filters.DateFilter(
        field_name='analysis_period_start',
        lookup_expr='lte',
    )

    class Meta:
        model = TrendAnalysis
        fields = [
            'status',
            'trend_direction',
            'statistical_method',
            'pms_plan',
            'product_line',
            'analyzed_by',
            'threshold_breached',
        ]


class PMSReportFilterSet(filters.FilterSet):
    """FilterSet for PMSReport"""

    status = filters.MultipleChoiceFilter(
        choices=PMSReport.STATUS_CHOICES,
    )
    report_type = filters.MultipleChoiceFilter(
        choices=PMSReport.REPORT_TYPE_CHOICES,
    )
    submitted_to = filters.MultipleChoiceFilter(
        choices=PMSReport.SUBMITTED_TO_CHOICES,
    )
    pms_plan = filters.NumberFilter(field_name='pms_plan__id')
    product_line = filters.NumberFilter(field_name='product_line__id')
    approved_by = filters.NumberFilter(field_name='approved_by__id')
    period_start_after = filters.DateFilter(
        field_name='period_start',
        lookup_expr='gte',
    )
    period_start_before = filters.DateFilter(
        field_name='period_start',
        lookup_expr='lte',
    )

    class Meta:
        model = PMSReport
        fields = [
            'status',
            'report_type',
            'submitted_to',
            'pms_plan',
            'product_line',
            'approved_by',
        ]


class VigilanceReportFilterSet(filters.FilterSet):
    """FilterSet for VigilanceReport"""

    status = filters.MultipleChoiceFilter(
        choices=VigilanceReport.STATUS_CHOICES,
    )
    authority = filters.MultipleChoiceFilter(
        choices=VigilanceReport.AUTHORITY_CHOICES,
    )
    report_type = filters.MultipleChoiceFilter(
        choices=VigilanceReport.REPORT_TYPE_CHOICES,
    )
    report_form = filters.MultipleChoiceFilter(
        choices=VigilanceReport.REPORT_FORM_CHOICES,
    )
    patient_outcome = filters.MultipleChoiceFilter(
        choices=VigilanceReport.PATIENT_OUTCOME_CHOICES,
    )
    submitted_by = filters.NumberFilter(field_name='submitted_by__id')
    submission_deadline_after = filters.DateFilter(
        field_name='submission_deadline',
        lookup_expr='gte',
    )
    submission_deadline_before = filters.DateFilter(
        field_name='submission_deadline',
        lookup_expr='lte',
    )

    class Meta:
        model = VigilanceReport
        fields = [
            'status',
            'authority',
            'report_type',
            'report_form',
            'patient_outcome',
            'submitted_by',
        ]


class LiteratureReviewFilterSet(filters.FilterSet):
    """FilterSet for LiteratureReview"""

    status = filters.MultipleChoiceFilter(
        choices=LiteratureReview.STATUS_CHOICES,
    )
    pms_plan = filters.NumberFilter(field_name='pms_plan__id')
    reviewed_by = filters.NumberFilter(field_name='reviewed_by__id')
    safety_signals_identified = filters.BooleanFilter()
    search_date_after = filters.DateFilter(
        field_name='search_date',
        lookup_expr='gte',
    )
    search_date_before = filters.DateFilter(
        field_name='search_date',
        lookup_expr='lte',
    )

    class Meta:
        model = LiteratureReview
        fields = [
            'status',
            'pms_plan',
            'reviewed_by',
            'safety_signals_identified',
        ]


class SafetySignalFilterSet(filters.FilterSet):
    """FilterSet for SafetySignal"""

    status = filters.MultipleChoiceFilter(
        choices=SafetySignal.STATUS_CHOICES,
    )
    source = filters.MultipleChoiceFilter(
        choices=SafetySignal.SOURCE_CHOICES,
    )
    severity = filters.MultipleChoiceFilter(
        choices=SafetySignal.SEVERITY_CHOICES,
    )
    product_line = filters.NumberFilter(field_name='product_line__id')
    evaluated_by = filters.NumberFilter(field_name='evaluated_by__id')
    linked_pms_plan = filters.NumberFilter(field_name='linked_pms_plan__id')
    detection_date_after = filters.DateFilter(
        field_name='detection_date',
        lookup_expr='gte',
    )
    detection_date_before = filters.DateFilter(
        field_name='detection_date',
        lookup_expr='lte',
    )

    class Meta:
        model = SafetySignal
        fields = [
            'status',
            'source',
            'severity',
            'product_line',
            'evaluated_by',
            'linked_pms_plan',
        ]
