"""
Workflow Engine signals.
Auto-initialize workflows when EQMS records are created.
Auto-update overdue status.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from .services import WorkflowService, WorkflowError

logger = logging.getLogger('workflows.signals')

# Mapping of model_type to (workflow_name, app_label, model_name)
WORKFLOW_MAP = {
    'document': ('Document Lifecycle', 'documents', 'Document'),
    'capa': ('CAPA Lifecycle', 'capa', 'CAPA'),
    'deviation': ('Deviation Workflow', 'deviations', 'Deviation'),
    'complaint': ('Complaint Workflow', 'complaints', 'Complaint'),
    'change_control': ('Change Control Workflow', 'change_controls', 'ChangeControl'),
}


def auto_initialize_workflow(sender, instance, created, **kwargs):
    """
    Auto-initialize a workflow when a new EQMS record is created.
    Only triggers on creation (not updates).
    """
    if not created:
        return

    # Determine model_type from sender
    model_name = sender.__name__
    model_type = None
    workflow_name = None

    for mtype, (wf_name, app_label, mname) in WORKFLOW_MAP.items():
        if mname == model_name:
            model_type = mtype
            workflow_name = wf_name
            break

    if not model_type:
        return

    # Check if workflow already exists for this record
    from .models import WorkflowRecord
    from django.contrib.contenttypes.models import ContentType
    ct = ContentType.objects.get_for_model(instance)
    existing = WorkflowRecord.objects.filter(
        content_type=ct, object_id=str(instance.pk)
    ).exists()

    if existing:
        return

    # Get the user who created the record
    user = getattr(instance, 'created_by', None)
    if not user:
        user = getattr(instance, 'owner', None) or getattr(instance, 'initiator', None)
    if not user:
        logger.warning(
            f"Cannot auto-initialize workflow for {instance}: no user found"
        )
        return

    try:
        workflow_record = WorkflowService.initialize_workflow(
            record=instance,
            workflow_name=workflow_name,
            model_type=model_type,
            user=user,
        )
        logger.info(
            f"Auto-initialized workflow '{workflow_name}' for {instance} "
            f"at stage '{workflow_record.current_stage.name}'"
        )
    except WorkflowError as e:
        logger.warning(
            f"Failed to auto-initialize workflow for {instance}: {e}"
        )
    except Exception as e:
        logger.error(
            f"Unexpected error initializing workflow for {instance}: {e}"
        )


def connect_workflow_signals():
    """
    Connect post_save signals for all EQMS models.
    Called from WorkflowsConfig.ready().
    """
    from django.apps import apps

    for model_type, (workflow_name, app_label, model_name) in WORKFLOW_MAP.items():
        try:
            model = apps.get_model(app_label, model_name)
            post_save.connect(
                auto_initialize_workflow,
                sender=model,
                dispatch_uid=f'workflow_init_{model_type}',
            )
            logger.info(f"Connected workflow signal for {app_label}.{model_name}")
        except LookupError:
            logger.warning(f"Model {app_label}.{model_name} not found, skipping signal")
