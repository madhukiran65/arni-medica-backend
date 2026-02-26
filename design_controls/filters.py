import django_filters
from django.contrib.auth.models import User
from users.models import Site
from .models import (
    DesignProject,
    UserNeed,
    DesignInput,
    DesignOutput,
    VVProtocol,
    DesignReview,
    DesignTransfer,
    TraceabilityLink,
)


class DesignProjectFilterSet(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=DesignProject.STATUS_CHOICES)
    current_phase = django_filters.ChoiceFilter(choices=DesignProject.CURRENT_PHASE_CHOICES)
    product_type = django_filters.ChoiceFilter(choices=DesignProject.PRODUCT_TYPE_CHOICES)
    regulatory_pathway = django_filters.ChoiceFilter(choices=DesignProject.REGULATORY_PATHWAY_CHOICES)
    project_lead = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    target_completion_date_from = django_filters.DateFilter(
        field_name='target_completion_date', lookup_expr='gte'
    )
    target_completion_date_to = django_filters.DateFilter(
        field_name='target_completion_date', lookup_expr='lte'
    )

    class Meta:
        model = DesignProject
        fields = ['status', 'current_phase', 'product_type', 'regulatory_pathway', 'project_lead']


class UserNeedFilterSet(django_filters.FilterSet):
    project = django_filters.ModelChoiceFilter(queryset=DesignProject.objects.all())
    source = django_filters.ChoiceFilter(choices=UserNeed.SOURCE_CHOICES)
    priority = django_filters.ChoiceFilter(choices=UserNeed.PRIORITY_CHOICES)
    status = django_filters.ChoiceFilter(choices=UserNeed.STATUS_CHOICES)
    approved_by = django_filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )

    class Meta:
        model = UserNeed
        fields = ['project', 'source', 'priority', 'status', 'approved_by']


class DesignInputFilterSet(django_filters.FilterSet):
    project = django_filters.ModelChoiceFilter(queryset=DesignProject.objects.all())
    input_type = django_filters.ChoiceFilter(choices=DesignInput.INPUT_TYPE_CHOICES)
    status = django_filters.ChoiceFilter(choices=DesignInput.STATUS_CHOICES)
    approved_by = django_filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )

    class Meta:
        model = DesignInput
        fields = ['project', 'input_type', 'status', 'approved_by']


class DesignOutputFilterSet(django_filters.FilterSet):
    project = django_filters.ModelChoiceFilter(queryset=DesignProject.objects.all())
    output_type = django_filters.ChoiceFilter(choices=DesignOutput.OUTPUT_TYPE_CHOICES)
    status = django_filters.ChoiceFilter(choices=DesignOutput.STATUS_CHOICES)
    approved_by = django_filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )

    class Meta:
        model = DesignOutput
        fields = ['project', 'output_type', 'status', 'approved_by']


class VVProtocolFilterSet(django_filters.FilterSet):
    project = django_filters.ModelChoiceFilter(queryset=DesignProject.objects.all())
    protocol_type = django_filters.ChoiceFilter(choices=VVProtocol.PROTOCOL_TYPE_CHOICES)
    status = django_filters.ChoiceFilter(choices=VVProtocol.STATUS_CHOICES)
    result = django_filters.ChoiceFilter(choices=VVProtocol.RESULT_CHOICES)
    execution_date_from = django_filters.DateFilter(
        field_name='execution_date', lookup_expr='gte'
    )
    execution_date_to = django_filters.DateFilter(
        field_name='execution_date', lookup_expr='lte'
    )
    executed_by = django_filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    approved_by = django_filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )

    class Meta:
        model = VVProtocol
        fields = ['project', 'protocol_type', 'status', 'result', 'executed_by', 'approved_by']


class DesignReviewFilterSet(django_filters.FilterSet):
    project = django_filters.ModelChoiceFilter(queryset=DesignProject.objects.all())
    phase = django_filters.ChoiceFilter(choices=DesignReview.PHASE_CHOICES)
    status = django_filters.ChoiceFilter(choices=DesignReview.STATUS_CHOICES)
    outcome = django_filters.ChoiceFilter(choices=DesignReview.OUTCOME_CHOICES)
    review_date_from = django_filters.DateFilter(
        field_name='review_date', lookup_expr='gte'
    )
    review_date_to = django_filters.DateFilter(
        field_name='review_date', lookup_expr='lte'
    )

    class Meta:
        model = DesignReview
        fields = ['project', 'phase', 'status', 'outcome']


class DesignTransferFilterSet(django_filters.FilterSet):
    project = django_filters.ModelChoiceFilter(queryset=DesignProject.objects.all())
    status = django_filters.ChoiceFilter(choices=DesignTransfer.STATUS_CHOICES)
    manufacturing_site = django_filters.ModelChoiceFilter(
        queryset=Site.objects.all()
    )
    production_readiness_confirmed = django_filters.BooleanFilter()

    class Meta:
        model = DesignTransfer
        fields = ['project', 'status', 'manufacturing_site', 'production_readiness_confirmed']


class TraceabilityLinkFilterSet(django_filters.FilterSet):
    project = django_filters.ModelChoiceFilter(queryset=DesignProject.objects.all())
    link_status = django_filters.ChoiceFilter(choices=TraceabilityLink.LINK_STATUS_CHOICES)
    user_need = django_filters.ModelChoiceFilter(
        queryset=UserNeed.objects.all(), required=False
    )
    design_input = django_filters.ModelChoiceFilter(
        queryset=DesignInput.objects.all(), required=False
    )
    design_output = django_filters.ModelChoiceFilter(
        queryset=DesignOutput.objects.all(), required=False
    )
    vv_protocol = django_filters.ModelChoiceFilter(
        queryset=VVProtocol.objects.all(), required=False
    )

    class Meta:
        model = TraceabilityLink
        fields = ['project', 'link_status', 'user_need', 'design_input', 'design_output', 'vv_protocol']
