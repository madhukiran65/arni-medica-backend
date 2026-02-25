from django.contrib import admin
from .models import (
    WorkflowDefinition, WorkflowStage, WorkflowTransition,
    WorkflowRecord, WorkflowHistory, WorkflowApprovalGate,
    WorkflowApprovalRequest, WorkflowDelegation,
)


class WorkflowStageInline(admin.TabularInline):
    model = WorkflowStage
    extra = 1
    ordering = ['sequence']


class WorkflowTransitionInline(admin.TabularInline):
    model = WorkflowTransition
    extra = 1
    fk_name = 'workflow'


class WorkflowApprovalGateInline(admin.TabularInline):
    model = WorkflowApprovalGate
    extra = 0
    ordering = ['sequence']


@admin.register(WorkflowDefinition)
class WorkflowDefinitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_type', 'is_active', 'stage_count', 'created_at']
    list_filter = ['model_type', 'is_active']
    search_fields = ['name', 'description']
    inlines = [WorkflowStageInline, WorkflowTransitionInline]

    def stage_count(self, obj):
        return obj.stages.count()
    stage_count.short_description = 'Stages'


@admin.register(WorkflowStage)
class WorkflowStageAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'workflow', 'sequence', 'requires_approval',
        'requires_signature', 'is_initial', 'is_terminal', 'sla_days',
    ]
    list_filter = ['workflow', 'requires_approval', 'requires_signature', 'is_initial', 'is_terminal']
    inlines = [WorkflowApprovalGateInline]


@admin.register(WorkflowTransition)
class WorkflowTransitionAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'from_stage', 'to_stage', 'label', 'is_rejection']
    list_filter = ['workflow', 'is_rejection']


@admin.register(WorkflowRecord)
class WorkflowRecordAdmin(admin.ModelAdmin):
    list_display = [
        'content_type', 'object_id', 'workflow', 'current_stage',
        'entered_stage_at', 'is_overdue', 'is_active',
    ]
    list_filter = ['workflow', 'current_stage', 'is_overdue', 'is_active']
    readonly_fields = ['created_at', 'entered_stage_at']


@admin.register(WorkflowHistory)
class WorkflowHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'workflow_record', 'from_stage', 'to_stage',
        'transitioned_by', 'transitioned_at',
    ]
    list_filter = ['from_stage', 'to_stage']
    readonly_fields = [
        'workflow_record', 'from_stage', 'to_stage', 'transition',
        'transitioned_by', 'transitioned_at', 'comments', 'ip_address',
        'time_in_stage_seconds', 'signature',
    ]

    def has_change_permission(self, request, obj=None):
        return False  # Immutable

    def has_delete_permission(self, request, obj=None):
        return False  # Immutable


@admin.register(WorkflowApprovalRequest)
class WorkflowApprovalRequestAdmin(admin.ModelAdmin):
    list_display = [
        'approver', 'gate', 'status', 'requested_at', 'responded_at', 'due_date',
    ]
    list_filter = ['status', 'gate__stage']


@admin.register(WorkflowDelegation)
class WorkflowDelegationAdmin(admin.ModelAdmin):
    list_display = ['delegator', 'delegate', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']
