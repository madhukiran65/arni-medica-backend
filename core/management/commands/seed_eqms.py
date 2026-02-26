"""
Unified seed command for Arni Medica AI-EQMS.
Seeds: Workflows (with transitions + approval gates), InfoCard Types,
Job Functions, Departments, Roles, and Demo Data.

Based on MasterControl reference architecture + Dot Compliance UI patterns.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from documents.models import DocumentInfocardType
from training.models import JobFunction
from users.models import Department, Role, UserProfile
from workflows.seed_data import seed_all_workflows


class Command(BaseCommand):
    help = "Seed complete eQMS reference data (workflows, types, roles, demo data)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--demo', action='store_true',
            help='Also create demo records for testing'
        )
        parser.add_argument(
            '--reset-workflows', action='store_true',
            help='Delete existing workflows before re-seeding'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS(" Arni Medica AI-EQMS — Data Seeding"))
        self.stdout.write(self.style.SUCCESS("=" * 60))

        # 1. Departments
        dept_count = self._seed_departments()
        self.stdout.write(self.style.SUCCESS(f"  Departments: {dept_count} created"))

        # 2. Roles
        role_count = self._seed_roles()
        self.stdout.write(self.style.SUCCESS(f"  Roles: {role_count} created"))

        # 3. InfoCard Types (MasterControl-style)
        type_count = self._seed_infocard_types()
        self.stdout.write(self.style.SUCCESS(f"  InfoCard Types: {type_count} created"))

        # 4. Workflows (comprehensive — from workflows/seed_data.py)
        if options['reset_workflows']:
            from workflows.models import WorkflowDefinition
            deleted = WorkflowDefinition.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"  Reset: Deleted existing workflows"))
        seed_all_workflows()
        self.stdout.write(self.style.SUCCESS(f"  Workflows: Seeded (5 definitions)"))

        # 5. Job Functions
        jf_count = self._seed_job_functions()
        self.stdout.write(self.style.SUCCESS(f"  Job Functions: {jf_count} created"))

        # 6. User Profiles for existing users
        profile_count = self._ensure_user_profiles()
        self.stdout.write(self.style.SUCCESS(f"  User Profiles: {profile_count} ensured"))

        # 7. Demo data
        if options['demo']:
            demo_count = self._seed_demo_data()
            self.stdout.write(self.style.SUCCESS(f"  Demo Records: {demo_count} created"))

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS(" Seeding complete!"))
        self.stdout.write(self.style.SUCCESS("=" * 60))

    def _seed_departments(self):
        created = 0
        departments = [
            "Quality Assurance", "Quality Control", "Regulatory Affairs",
            "Research & Development", "Manufacturing", "Clinical Affairs",
            "Supply Chain", "Engineering", "Human Resources", "IT",
            "Marketing", "Sales", "Finance", "Management",
        ]
        for name in departments:
            _, is_new = Department.objects.get_or_create(
                name=name,
                defaults={"description": f"{name} department"}
            )
            if is_new:
                created += 1
        return created

    def _seed_roles(self):
        created = 0
        roles = [
            {
                "name": "Administrator",
                "can_create_documents": True, "can_approve_documents": True,
                "can_sign_documents": True, "can_create_capa": True,
                "can_close_capa": True, "can_create_complaints": True,
                "can_log_training": True, "can_create_audit": True,
                "can_view_audit_trail": True, "can_manage_users": True,
            },
            {
                "name": "QA Manager",
                "can_create_documents": True, "can_approve_documents": True,
                "can_sign_documents": True, "can_create_capa": True,
                "can_close_capa": True, "can_create_complaints": True,
                "can_log_training": True, "can_create_audit": True,
                "can_view_audit_trail": True, "can_manage_users": False,
            },
            {
                "name": "Document Controller",
                "can_create_documents": True, "can_approve_documents": True,
                "can_sign_documents": True, "can_create_capa": False,
                "can_close_capa": False, "can_create_complaints": False,
                "can_log_training": False, "can_create_audit": False,
                "can_view_audit_trail": True, "can_manage_users": False,
            },
            {
                "name": "Quality Engineer",
                "can_create_documents": True, "can_approve_documents": False,
                "can_sign_documents": False, "can_create_capa": True,
                "can_close_capa": False, "can_create_complaints": True,
                "can_log_training": True, "can_create_audit": False,
                "can_view_audit_trail": True, "can_manage_users": False,
            },
            {
                "name": "Training Coordinator",
                "can_create_documents": False, "can_approve_documents": False,
                "can_sign_documents": False, "can_create_capa": False,
                "can_close_capa": False, "can_create_complaints": False,
                "can_log_training": True, "can_create_audit": False,
                "can_view_audit_trail": False, "can_manage_users": False,
            },
            {
                "name": "Viewer",
                "can_create_documents": False, "can_approve_documents": False,
                "can_sign_documents": False, "can_create_capa": False,
                "can_close_capa": False, "can_create_complaints": False,
                "can_log_training": False, "can_create_audit": False,
                "can_view_audit_trail": False, "can_manage_users": False,
            },
        ]
        for role_data in roles:
            name = role_data.pop("name")
            _, is_new = Role.objects.get_or_create(
                name=name, defaults=role_data
            )
            if is_new:
                created += 1
        return created

    def _seed_infocard_types(self):
        """Seed 26 InfoCard Types matching MasterControl's categorization."""
        created = 0
        types = [
            ("SOP", "Standard Operating Procedure"),
            ("WI", "Work Instruction"),
            ("FRM", "Form"),
            ("DRW", "Drawing"),
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
            ("LBL", "Label / Artwork"),
            ("PKG", "Packaging / Artwork"),
            ("REG", "Regulatory"),
            ("TRN", "Training Material"),
            ("PLN", "Plan"),
            ("RPT", "Report"),
            ("GUD", "Guideline"),
            ("DSP", "Design Specification"),
            ("RIS", "Risk Assessment / FMEA"),
            ("DHF", "Design History File"),
            ("DMR", "Device Master Record"),
            ("BOM", "Bill of Materials"),
        ]
        for prefix, name in types:
            _, is_new = DocumentInfocardType.objects.get_or_create(
                prefix=prefix,
                defaults={
                    "name": name,
                    "description": f"{name} document type",
                    "is_active": True,
                }
            )
            if is_new:
                created += 1
        return created

    def _seed_job_functions(self):
        """Seed Job Functions matching MasterControl Training Module."""
        created = 0
        functions = [
            ("QM", "Quality Manager", "Oversees quality management system"),
            ("QE", "Quality Engineer", "Implements and maintains quality processes"),
            ("DC", "Document Controller", "Manages controlled document lifecycle"),
            ("RA", "Regulatory Affairs Specialist", "Manages regulatory submissions"),
            ("PO", "Production Operator", "Operates production equipment"),
            ("LT", "Lab Technician", "Performs laboratory testing"),
            ("DE", "Design Engineer", "Designs products and components"),
            ("WS", "Warehouse Specialist", "Manages inventory and warehousing"),
            ("QAD", "QA Director", "Directs quality assurance department"),
            ("IA", "Internal Auditor", "Conducts internal quality audits"),
            ("TC", "Training Coordinator", "Manages training assignments"),
            ("SM", "Supplier Manager", "Manages supplier quality"),
            ("MFG", "Manufacturing Supervisor", "Supervises manufacturing ops"),
            ("EH", "EHS Specialist", "Environment, Health & Safety"),
        ]
        for code, name, description in functions:
            _, is_new = JobFunction.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": description,
                    "is_active": True,
                }
            )
            if is_new:
                created += 1
        return created

    def _ensure_user_profiles(self):
        """Ensure all existing users have a UserProfile."""
        created = 0
        for user in User.objects.all():
            _, is_new = UserProfile.objects.get_or_create(
                user=user,
                defaults={"employee_id": f"EMP-{user.pk:04d}"}
            )
            if is_new:
                created += 1
        return created

    def _seed_demo_data(self):
        """Create demo records for each module to show the system in action."""
        from documents.models import Document
        from capa.models import CAPA
        from deviations.models import Deviation
        from complaints.models import Complaint
        from change_controls.models import ChangeControl

        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            self.stdout.write(self.style.WARNING("  No admin user found, skipping demo data"))
            return 0

        count = 0

        # Demo Documents
        doc_defaults = [
            {"title": "SOP-001: Equipment Calibration Procedure", "lifecycle_state": "draft"},
            {"title": "WI-001: Blood Sample Collection Guide", "lifecycle_state": "draft"},
            {"title": "FRM-001: Batch Record Template", "lifecycle_state": "draft"},
            {"title": "POL-001: Quality Policy Manual", "lifecycle_state": "draft"},
            {"title": "VAL-001: IQ/OQ/PQ Protocol for Glucose Analyzer", "lifecycle_state": "draft"},
        ]
        for doc_data in doc_defaults:
            _, is_new = Document.objects.get_or_create(
                title=doc_data["title"],
                defaults={
                    **doc_data,
                    "created_by": admin,
                    "updated_by": admin,
                    "owner": admin,
                    "description": f"Demo document: {doc_data['title']}",
                }
            )
            if is_new:
                count += 1

        # Demo CAPAs
        capa_defaults = [
            {"title": "CAPA-001: Out-of-Spec Glucose Test Results", "capa_type": "corrective", "priority": "high"},
            {"title": "CAPA-002: Recurring Labeling Errors", "capa_type": "preventive", "priority": "medium"},
            {"title": "CAPA-003: Supplier Material Non-Conformance", "capa_type": "corrective", "priority": "critical"},
        ]
        for capa_data in capa_defaults:
            _, is_new = CAPA.objects.get_or_create(
                title=capa_data["title"],
                defaults={
                    **capa_data,
                    "created_by": admin,
                    "updated_by": admin,
                    "initiator": admin,
                    "owner": admin,
                    "description": f"Demo CAPA: {capa_data['title']}",
                    "source": "internal_audit",
                }
            )
            if is_new:
                count += 1

        self.stdout.write(f"  Created {count} demo records")
        return count
