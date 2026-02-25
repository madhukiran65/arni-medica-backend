from django.core.management.base import BaseCommand
from documents.models import DocumentInfocardType
from workflows.models import WorkflowDefinition, WorkflowStage
from training.models import JobFunction


class Command(BaseCommand):
    help = "Seed initial eQMS reference data for Arni Medica"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting eQMS data seeding..."))

        infocard_count = self.seed_document_infocard_types()
        workflow_count = self.seed_workflow_definitions()
        stage_count = self.seed_workflow_stages()
        job_count = self.seed_job_functions()

        self.stdout.write(self.style.SUCCESS(
            f"\nSeeding complete! Created: "
            f"{infocard_count} infocard types, {workflow_count} workflows, "
            f"{stage_count} stages, {job_count} job functions"
        ))

    def seed_document_infocard_types(self):
        """Seed 26 Document Infocard Types"""
        created = 0
        types = [
            ("SOP", "Standard Operating Procedure"),
            ("INR", "Internal Report"),
            ("WIS", "Work Instruction Sheet"),
            ("DRW", "Drawing"),
            ("FRM", "Form"),
            ("SPE", "Specification"),
            ("POL", "Policy"),
            ("MAN", "Manual"),
            ("TMP", "Template"),
            ("LOG", "Log"),
            ("CHK", "Checklist"),
            ("PRO", "Protocol"),
            ("VAL", "Validation"),
            ("CER", "Certificate"),
            ("AGR", "Agreement"),
            ("LBL", "Label"),
            ("PKG", "Packaging"),
            ("REG", "Regulatory"),
            ("TRN", "Training"),
            ("PLN", "Plan"),
            ("RPT", "Report"),
            ("GUD", "Guideline"),
            ("DSP", "Design Specification"),
            ("RIS", "Risk Analysis"),
            ("DHF", "Design History File"),
            ("DMR", "Device Master Record"),
        ]
        for prefix, name in types:
            obj, is_new = DocumentInfocardType.objects.get_or_create(
                prefix=prefix,
                defaults={
                    "name": name,
                    "description": f"{name} document type",
                    "is_active": True,
                }
            )
            if is_new:
                created += 1
                self.stdout.write(f"  Created: {prefix} - {name}")
        return created

    def seed_workflow_definitions(self):
        """Seed Workflow Definitions for each module"""
        created = 0
        definitions = [
            ("Document Review & Approval", "document", "Standard document lifecycle workflow"),
            ("CAPA Lifecycle", "capa", "Corrective and Preventive Actions workflow"),
            ("Complaint Handling", "complaint", "Customer complaint investigation and resolution"),
            ("Deviation Management", "deviation", "Deviation investigation and closure"),
            ("Change Control Process", "change_control", "Change control assessment and implementation"),
        ]
        for name, model_type, description in definitions:
            obj, is_new = WorkflowDefinition.objects.get_or_create(
                name=name,
                model_type=model_type,
                defaults={"description": description, "is_active": True}
            )
            if is_new:
                created += 1
                self.stdout.write(f"  Created workflow: {name}")
        return created

    def seed_workflow_stages(self):
        """Seed Workflow Stages for each definition"""
        created = 0
        stage_configs = {
            "Document Review & Approval": [
                (1, "draft", "Draft", "#9CA3AF", False),
                (2, "in_review", "In Review", "#3B82F6", False),
                (3, "qa_review", "QA Review", "#F59E0B", True),
                (4, "approved", "Approved", "#10B981", True),
                (5, "released", "Released", "#059669", False),
                (6, "obsolete", "Obsolete", "#EF4444", False),
            ],
            "CAPA Lifecycle": [
                (1, "initiation", "Initiation", "#9CA3AF", False),
                (2, "investigation", "Investigation", "#3B82F6", False),
                (3, "root_cause", "Root Cause Analysis", "#F59E0B", True),
                (4, "action_plan", "Action Plan", "#8B5CF6", False),
                (5, "implementation", "Implementation", "#06B6D4", False),
                (6, "effectiveness", "Effectiveness Check", "#10B981", True),
                (7, "closure", "Closure", "#059669", True),
            ],
            "Complaint Handling": [
                (1, "intake", "Intake", "#9CA3AF", False),
                (2, "investigation", "Investigation", "#3B82F6", False),
                (3, "reportability", "Reportability Determination", "#F59E0B", True),
                (4, "resolution", "Resolution", "#10B981", False),
                (5, "closure", "Closure", "#059669", True),
            ],
            "Deviation Management": [
                (1, "reported", "Reported", "#9CA3AF", False),
                (2, "assessment", "Initial Assessment", "#3B82F6", False),
                (3, "investigation", "Investigation", "#F59E0B", False),
                (4, "capa_determination", "CAPA Determination", "#8B5CF6", True),
                (5, "resolution", "Resolution", "#10B981", False),
                (6, "closure", "Closure", "#059669", True),
            ],
            "Change Control Process": [
                (1, "request", "Change Request", "#9CA3AF", False),
                (2, "impact_assessment", "Impact Assessment", "#3B82F6", False),
                (3, "technical_review", "Technical Review", "#F59E0B", True),
                (4, "approval", "Approval", "#8B5CF6", True),
                (5, "implementation", "Implementation", "#06B6D4", False),
                (6, "verification", "Verification", "#10B981", True),
                (7, "closure", "Closure", "#059669", False),
            ],
        }
        for wf_name, stages in stage_configs.items():
            try:
                wf = WorkflowDefinition.objects.get(name=wf_name)
            except WorkflowDefinition.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  Workflow not found: {wf_name}"))
                continue
            for sequence, slug, name, color, requires_approval in stages:
                obj, is_new = WorkflowStage.objects.get_or_create(
                    workflow=wf,
                    slug=slug,
                    defaults={
                        "name": name,
                        "sequence": sequence,
                        "color": color,
                        "requires_approval": requires_approval,
                    }
                )
                if is_new:
                    created += 1
                    self.stdout.write(f"  Created stage: {wf_name} -> {name}")
        return created

    def seed_job_functions(self):
        """Seed Job Functions for training management"""
        created = 0
        functions = [
            ("QM", "Quality Manager", "Oversees quality management system"),
            ("QE", "Quality Engineer", "Implements and maintains quality processes"),
            ("PO", "Production Operator", "Operates production equipment"),
            ("LT", "Lab Technician", "Performs laboratory testing"),
            ("RA", "Regulatory Affairs Specialist", "Manages regulatory submissions"),
            ("DE", "Design Engineer", "Designs products and components"),
            ("WS", "Warehouse Specialist", "Manages inventory and warehousing"),
            ("QAD", "Quality Assurance Director", "Directs quality assurance department"),
        ]
        for code, name, description in functions:
            obj, is_new = JobFunction.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": description,
                    "is_active": True,
                }
            )
            if is_new:
                created += 1
                self.stdout.write(f"  Created job function: {code} - {name}")
        return created
