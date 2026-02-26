"""
Management command to add the 'Superseded' stage to the Document Lifecycle workflow.
In regulated eQMS environments (like Dot Compliance), Superseded means the document
has been replaced by a newer version but is retained for traceability per ISO 13485.
"""
from django.core.management.base import BaseCommand
from workflows.models import WorkflowDefinition, WorkflowStage, WorkflowTransition


class Command(BaseCommand):
    help = 'Add Superseded stage to Document Lifecycle workflow'

    def handle(self, *args, **options):
        try:
            wf = WorkflowDefinition.objects.get(id=10, model_type='document')
        except WorkflowDefinition.DoesNotExist:
            self.stderr.write('Document Lifecycle workflow (ID=10) not found')
            return

        # Check if already exists
        if WorkflowStage.objects.filter(workflow=wf, slug='superseded').exists():
            self.stdout.write('Superseded stage already exists — skipping creation')
            superseded = WorkflowStage.objects.get(workflow=wf, slug='superseded')
        else:
            # Bump Archived first (to 8), then Obsolete (to 7) to avoid unique constraint
            obsolete = WorkflowStage.objects.get(workflow=wf, slug='obsolete')
            archived = WorkflowStage.objects.get(workflow=wf, slug='archived')

            # Must update in reverse order to avoid unique constraint on (workflow_id, sequence)
            archived.sequence = 8
            archived.save(update_fields=['sequence'])
            self.stdout.write(f'  Archived bumped to sequence {archived.sequence}')

            obsolete.sequence = 7
            obsolete.save(update_fields=['sequence'])
            self.stdout.write(f'  Obsolete bumped to sequence {obsolete.sequence}')

            # Create Superseded stage
            superseded = WorkflowStage.objects.create(
                workflow=wf,
                name='Superseded',
                slug='superseded',
                sequence=6,
                description=(
                    'Document has been replaced by a newer version. '
                    'Retained for traceability and reference per ISO 13485 Clause 4.2.4.'
                ),
                color='#F97316',  # Orange — distinct from Released (green) and Obsolete (red)
                requires_approval=False,
                requires_signature=False,
                is_initial=False,
                is_terminal=False,
                allows_edit=False,
                auto_advance=False,
            )
            self.stdout.write(f'  Created Superseded stage (ID: {superseded.id}, seq: 6)')

        # Update workflow stage_count
        wf.description = 'Standard document lifecycle workflow (8 stages, incl. Superseded)'
        wf.save(update_fields=['description'])

        # Get stage references
        released = WorkflowStage.objects.get(workflow=wf, slug='released')
        obsolete = WorkflowStage.objects.get(workflow=wf, slug='obsolete')
        archived = WorkflowStage.objects.get(workflow=wf, slug='archived')

        # Create transitions
        transitions_to_create = [
            {
                'from_stage': released,
                'to_stage': superseded,
                'label': 'Supersede',
                'description': 'Mark as superseded when a newer version is released',
                'button_color': '#F97316',
                'is_rejection': False,
            },
            {
                'from_stage': superseded,
                'to_stage': archived,
                'label': 'Archive',
                'description': 'Archive superseded document for long-term retention',
                'button_color': '#6B7280',
                'is_rejection': False,
            },
            {
                'from_stage': superseded,
                'to_stage': obsolete,
                'label': 'Mark Obsolete',
                'description': 'Mark superseded document as obsolete (actively withdrawn)',
                'button_color': '#EF4444',
                'is_rejection': False,
            },
        ]

        for t_data in transitions_to_create:
            t, created = WorkflowTransition.objects.get_or_create(
                workflow=wf,
                from_stage=t_data['from_stage'],
                to_stage=t_data['to_stage'],
                defaults={
                    'label': t_data['label'],
                    'description': t_data['description'],
                    'button_color': t_data['button_color'],
                    'is_rejection': t_data['is_rejection'],
                }
            )
            action = 'Created' if created else 'Already exists'
            self.stdout.write(
                f'  {action}: {t_data["from_stage"].name} → {t_data["to_stage"].name} '
                f'("{t_data["label"]}")'
            )

        # Summary
        all_stages = list(
            WorkflowStage.objects.filter(workflow=wf)
            .order_by('sequence')
            .values_list('name', flat=True)
        )
        self.stdout.write(self.style.SUCCESS(
            f'\nDocument Lifecycle now has {len(all_stages)} stages: '
            + ' → '.join(all_stages)
        ))
