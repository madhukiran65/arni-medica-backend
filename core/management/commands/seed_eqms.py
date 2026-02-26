"""
Unified seed command for Arni Medica AI-EQMS.
Seeds: Workflows (with transitions + approval gates), InfoCard Types,
Job Functions, Departments, Roles, Demo Data, and supporting entities.

Based on MasterControl reference architecture + Dot Compliance UI patterns.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

from documents.models import DocumentInfocardType, Document
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
        parser.add_argument(
            '--reset-demo', action='store_true',
            help='Delete all demo data before re-seeding'
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
        from workflows.models import WorkflowDefinition
        if options['reset_workflows']:
            deleted = WorkflowDefinition.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"  Reset: Deleted existing workflows"))
        else:
            # Clean up duplicates — keep only the canonical 5 definitions from seed_data.py
            # Delete old-style workflows that don't match the canonical names
            canonical_names = {
                'Document Lifecycle', 'CAPA Lifecycle', 'Deviation Workflow',
                'Complaint Workflow', 'Change Control Workflow',
            }
            old_wfs = WorkflowDefinition.objects.exclude(name__in=canonical_names)
            if old_wfs.exists():
                count = old_wfs.count()
                old_wfs.delete()
                self.stdout.write(self.style.WARNING(f"  Cleanup: Deleted {count} duplicate workflows"))
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
            if options['reset_demo']:
                self._reset_demo_data()
                self.stdout.write(self.style.WARNING(f"  Reset: Deleted existing demo data"))
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

    def _reset_demo_data(self):
        """Delete all demo data records."""
        from documents.models import Document
        from capa.models import CAPA
        from deviations.models import Deviation
        from complaints.models import Complaint
        from change_controls.models import ChangeControl

        # Delete in order of dependencies (reverse of creation order)
        ChangeControl.objects.all().delete()
        Complaint.objects.all().delete()
        Deviation.objects.all().delete()
        CAPA.objects.all().delete()
        Document.objects.all().delete()

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

        # Get departments and infocard types for FK assignments
        qa_dept = Department.objects.filter(name="Quality Assurance").first()
        qa_control_dept = Department.objects.filter(name="Quality Control").first()
        manufacturing_dept = Department.objects.filter(name="Manufacturing").first()
        regulatory_dept = Department.objects.filter(name="Regulatory Affairs").first()
        rd_dept = Department.objects.filter(name="Research & Development").first()

        # Demo Documents - 10 documents with proper infocard_type FK lookups
        doc_specs = [
            {
                "title": "SOP-001: Equipment Calibration Procedure",
                "prefix": "SOP",
                "vault_state": "released",
                "department": qa_dept,
                "requires_training": True,
                "review_period_months": 24,
            },
            {
                "title": "WI-001: Blood Sample Collection Guide",
                "prefix": "WI",
                "vault_state": "released",
                "department": manufacturing_dept,
                "requires_training": True,
                "review_period_months": 12,
            },
            {
                "title": "FRM-001: Batch Record Template",
                "prefix": "FRM",
                "vault_state": "released",
                "department": manufacturing_dept,
                "requires_training": False,
                "review_period_months": 36,
            },
            {
                "title": "POL-001: Quality Policy Manual",
                "prefix": "POL",
                "vault_state": "released",
                "department": qa_dept,
                "requires_training": True,
                "review_period_months": 24,
            },
            {
                "title": "VAL-001: IQ/OQ/PQ Protocol for Glucose Analyzer",
                "prefix": "VAL",
                "vault_state": "draft",
                "department": rd_dept,
                "requires_training": False,
                "review_period_months": 60,
            },
            {
                "title": "SPE-001: Reagent Specifications",
                "prefix": "SPE",
                "vault_state": "released",
                "department": manufacturing_dept,
                "requires_training": False,
                "review_period_months": 36,
            },
            {
                "title": "PRO-001: Method Validation Protocol",
                "prefix": "PRO",
                "vault_state": "released",
                "department": qa_control_dept,
                "requires_training": False,
                "review_period_months": 48,
            },
            {
                "title": "CHK-001: Equipment Maintenance Checklist",
                "prefix": "CHK",
                "vault_state": "archived",
                "department": manufacturing_dept,
                "requires_training": False,
                "review_period_months": 12,
            },
            {
                "title": "REG-001: FDA Compliance Documentation",
                "prefix": "REG",
                "vault_state": "released",
                "department": regulatory_dept,
                "requires_training": False,
                "review_period_months": 24,
            },
            {
                "title": "TRN-001: Annual Operator Training Material",
                "prefix": "TRN",
                "vault_state": "released",
                "department": qa_dept,
                "requires_training": True,
                "review_period_months": 12,
            },
        ]

        for doc_spec in doc_specs:
            prefix = doc_spec.pop("prefix")
            infocard_type = DocumentInfocardType.objects.filter(prefix=prefix).first()
            if not infocard_type:
                self.stdout.write(self.style.WARNING(f"  Warning: Infocard type {prefix} not found"))
                continue

            today = timezone.now().date()
            effective_date = today - timedelta(days=30)
            next_review_date = today + timedelta(days=365)

            defaults = {
                **doc_spec,
                "infocard_type": infocard_type,
                "created_by": admin,
                "updated_by": admin,
                "owner": admin,
                "description": f"Demo document: {doc_spec['title']}",
                "effective_date": effective_date,
                "next_review_date": next_review_date,
                "confidentiality_level": "internal",
                "distribution_restriction": "internal",
            }

            _, is_new = Document.objects.get_or_create(
                title=doc_spec["title"],
                defaults=defaults
            )
            if is_new:
                count += 1

        # Demo CAPAs - 8 CAPAs with assigned_to, target dates, various phases
        capa_specs = [
            {
                "title": "CAPA-001: Out-of-Spec Glucose Test Results",
                "capa_type": "corrective",
                "priority": "high",
                "category": "product",
                "current_phase": "investigation",
                "source": "internal_observation",
                "what_happened": "Multiple glucose test results exceeded specification limits",
                "where_happened": "Lab Unit 3",
                "target_completion_date": timezone.now().date() + timedelta(days=30),
            },
            {
                "title": "CAPA-002: Recurring Labeling Errors",
                "capa_type": "preventive",
                "priority": "medium",
                "category": "documentation",
                "current_phase": "capa_plan",
                "source": "audit",
                "what_happened": "Inconsistent label application during packaging",
                "where_happened": "Packaging Department",
                "target_completion_date": timezone.now().date() + timedelta(days=45),
            },
            {
                "title": "CAPA-003: Supplier Material Non-Conformance",
                "capa_type": "corrective",
                "priority": "critical",
                "category": "supplier",
                "current_phase": "root_cause",
                "source": "regulatory",
                "what_happened": "Supplier delivered material with impurities",
                "where_happened": "Incoming Quality Control",
                "target_completion_date": timezone.now().date() + timedelta(days=14),
            },
            {
                "title": "CAPA-004: System Data Integrity Issue",
                "capa_type": "corrective",
                "priority": "high",
                "category": "system",
                "current_phase": "investigation",
                "source": "management_review",
                "what_happened": "System logs showing data synchronization failures",
                "where_happened": "IT Infrastructure",
                "target_completion_date": timezone.now().date() + timedelta(days=21),
            },
            {
                "title": "CAPA-005: Temperature Excursion Prevention",
                "capa_type": "preventive",
                "priority": "high",
                "category": "equipment",
                "current_phase": "capa_plan",
                "source": "internal_observation",
                "what_happened": "Cold storage unit experienced minor temperature fluctuations",
                "where_happened": "Warehouse Storage",
                "target_completion_date": timezone.now().date() + timedelta(days=60),
            },
            {
                "title": "CAPA-006: Training Records Completeness",
                "capa_type": "preventive",
                "priority": "medium",
                "category": "training",
                "current_phase": "effectiveness",
                "source": "audit",
                "what_happened": "Some training records missing completion dates",
                "where_happened": "Human Resources",
                "target_completion_date": timezone.now().date() + timedelta(days=30),
            },
            {
                "title": "CAPA-007: Documentation Process Improvement",
                "capa_type": "preventive",
                "priority": "low",
                "category": "process",
                "current_phase": "implementation",
                "source": "customer_feedback",
                "what_happened": "Customer requested clearer installation instructions",
                "where_happened": "Documentation Team",
                "target_completion_date": timezone.now().date() + timedelta(days=90),
            },
            {
                "title": "CAPA-008: Quality Control Sampling Plan",
                "capa_type": "preventive",
                "priority": "medium",
                "category": "process",
                "current_phase": "root_cause",
                "source": "inspection",
                "what_happened": "Review of sampling plan revealed gaps in coverage",
                "where_happened": "Quality Control Department",
                "target_completion_date": timezone.now().date() + timedelta(days=45),
            },
        ]

        for capa_spec in capa_specs:
            defaults = {
                **capa_spec,
                "created_by": admin,
                "updated_by": admin,
                "department": qa_dept,
                "assigned_to": admin,
                "coordinator": admin,
                "description": f"Demo CAPA: {capa_spec['title']}",
                "risk_severity": 3,
                "risk_occurrence": 2,
                "risk_detection": 3,
            }

            _, is_new = CAPA.objects.get_or_create(
                title=capa_spec["title"],
                defaults=defaults
            )
            if is_new:
                count += 1

        # Demo Deviations - 6 deviations with various severities and stages
        deviation_specs = [
            {
                "title": "DEV-001: Out-of-Specification Test Result",
                "description": "Blood glucose analyzer produced OOS result for control sample",
                "deviation_type": "unplanned",
                "category": "product",
                "severity": "critical",
                "source": "qa_inspection",
                "process_affected": "Quality Control Testing",
                "product_affected": "Glucose Analyzer Model X-2000",
                "batch_lot_number": "LOT-2024-12345",
                "impact_assessment": "Potential patient safety risk if unreliable results reached patients",
                "patient_safety_impact": True,
                "current_stage": "investigation",
                "department": qa_control_dept,
                "reported_by": admin,
                "assigned_to": admin,
                "target_closure_date": timezone.now() + timedelta(days=30),
            },
            {
                "title": "DEV-002: Missing Equipment Calibration",
                "description": "Pipette calibration overdue during routine audit",
                "deviation_type": "planned",
                "category": "equipment",
                "severity": "major",
                "source": "internal_audit",
                "process_affected": "Equipment Maintenance",
                "product_affected": "Lab Equipment",
                "impact_assessment": "Measurement accuracy may be compromised",
                "patient_safety_impact": False,
                "current_stage": "qa_review",
                "department": manufacturing_dept,
                "reported_by": admin,
                "assigned_to": admin,
                "target_closure_date": timezone.now() + timedelta(days=7),
            },
            {
                "title": "DEV-003: Documentation Discrepancy",
                "description": "Procedure step numbers do not match in current vs archived versions",
                "deviation_type": "unplanned",
                "category": "documentation",
                "severity": "minor",
                "source": "self_inspection",
                "process_affected": "Document Control",
                "product_affected": "Training Materials",
                "impact_assessment": "Potential confusion during operator training",
                "patient_safety_impact": False,
                "current_stage": "capa_plan",
                "department": qa_dept,
                "reported_by": admin,
                "assigned_to": admin,
                "target_closure_date": timezone.now() + timedelta(days=14),
            },
            {
                "title": "DEV-004: Temperature Storage Excursion",
                "description": "Refrigerator temperature exceeded range by 2 degrees for 4 hours",
                "deviation_type": "unplanned",
                "category": "environmental",
                "severity": "major",
                "source": "production",
                "process_affected": "Material Storage",
                "product_affected": "Temperature-Sensitive Reagents",
                "batch_lot_number": "REG-2024-00567",
                "impact_assessment": "Potential reagent degradation affecting test results",
                "patient_safety_impact": True,
                "current_stage": "investigation",
                "department": manufacturing_dept,
                "reported_by": admin,
                "assigned_to": admin,
                "target_closure_date": timezone.now() + timedelta(days=21),
            },
            {
                "title": "DEV-005: Supplier Non-Conformance",
                "description": "Received material batch with visible contamination",
                "deviation_type": "unplanned",
                "category": "material",
                "severity": "critical",
                "source": "customer_complaint",
                "process_affected": "Procurement Quality",
                "product_affected": "Raw Materials for Assembly",
                "batch_lot_number": "SUP-2024-98765",
                "impact_assessment": "Could result in product quality issues if used",
                "patient_safety_impact": True,
                "current_stage": "pending_capa_approval",
                "department": manufacturing_dept,
                "reported_by": admin,
                "assigned_to": admin,
                "target_closure_date": timezone.now() + timedelta(days=10),
            },
            {
                "title": "DEV-006: Training Record Incomplete",
                "description": "Operator training completion form missing supervisor signature",
                "deviation_type": "planned",
                "category": "documentation",
                "severity": "minor",
                "source": "self_inspection",
                "process_affected": "Training Administration",
                "product_affected": "Training System",
                "impact_assessment": "Insufficient documentation of operator qualification",
                "patient_safety_impact": False,
                "current_stage": "completed",
                "department": qa_dept,
                "reported_by": admin,
                "assigned_to": admin,
                "target_closure_date": timezone.now() - timedelta(days=1),
            },
        ]

        for dev_spec in deviation_specs:
            defaults = {
                **dev_spec,
                "created_by": admin,
                "updated_by": admin,
            }

            _, is_new = Deviation.objects.get_or_create(
                title=dev_spec["title"],
                defaults=defaults
            )
            if is_new:
                count += 1

        # Demo Complaints - 6 complaints with various categories and event types
        complaint_specs = [
            {
                "title": "CMP-001: Glucose Analyzer Malfunction",
                "description": "Customer reports analyzer producing inconsistent results after software update",
                "complainant_name": "Dr. Smith",
                "complainant_email": "dr.smith@hospital.com",
                "complainant_type": "healthcare_provider",
                "product_name": "Glucose Analyzer X-2000",
                "product_code": "GA-2000-001",
                "product_lot_number": "LOT-2024-11111",
                "event_date": timezone.now().date() - timedelta(days=5),
                "event_description": "Device stopped responding after receiving firmware update",
                "event_location": "City Hospital Laboratory",
                "event_country": "United States",
                "category": "product_performance",
                "severity": "major",
                "priority": "high",
                "event_type": "malfunction",
                "status": "under_investigation",
                "assigned_to": admin,
                "target_closure_date": timezone.now().date() + timedelta(days=30),
            },
            {
                "title": "CMP-002: Missing Instructions in Package",
                "description": "Customer received product without installation manual",
                "complainant_name": "John Doe",
                "complainant_email": "john@clinic.org",
                "complainant_type": "customer",
                "product_name": "Rapid Test Kit",
                "product_code": "RTK-100",
                "product_lot_number": "LOT-2024-22222",
                "event_date": timezone.now().date() - timedelta(days=2),
                "event_description": "Package was incomplete, missing documentation",
                "event_location": "Regional Clinic",
                "event_country": "Canada",
                "category": "labeling",
                "severity": "minor",
                "priority": "medium",
                "event_type": "other",
                "status": "new",
                "assigned_to": admin,
                "target_closure_date": timezone.now().date() + timedelta(days=14),
            },
            {
                "title": "CMP-003: Reagent Discoloration",
                "description": "Opened reagent bottle showed unusual color, may indicate degradation",
                "complainant_name": "Lab Manager",
                "complainant_email": "lab.mgr@testing.com",
                "complainant_type": "customer",
                "product_name": "Quality Control Reagent",
                "product_code": "QCR-500",
                "product_lot_number": "LOT-2024-33333",
                "event_date": timezone.now().date() - timedelta(days=1),
                "event_description": "Reagent appeared discolored upon opening",
                "event_location": "Testing Laboratory",
                "event_country": "United States",
                "category": "product_quality",
                "severity": "major",
                "priority": "high",
                "event_type": "malfunction",
                "status": "under_investigation",
                "assigned_to": admin,
                "target_closure_date": timezone.now().date() + timedelta(days=7),
            },
            {
                "title": "CMP-004: Patient Safety Concern",
                "description": "Device may have caused serious injury due to improper calibration",
                "complainant_name": "Medical Examiner",
                "complainant_email": "medexam@hospital.com",
                "complainant_type": "healthcare_provider",
                "product_name": "Diagnostic Device Y-5000",
                "product_code": "DD-5000-01",
                "product_lot_number": "LOT-2024-44444",
                "event_date": timezone.now().date() - timedelta(days=10),
                "event_description": "Device reading led to incorrect diagnosis, patient hospitalized",
                "event_location": "Major Medical Center",
                "event_country": "United States",
                "category": "product_performance",
                "severity": "critical",
                "priority": "critical",
                "event_type": "serious_injury",
                "status": "capa_initiated",
                "assigned_to": admin,
                "target_closure_date": timezone.now().date() + timedelta(days=5),
            },
            {
                "title": "CMP-005: Packaging Damaged in Transit",
                "description": "Product arrived with damaged outer packaging, contents appear unaffected",
                "complainant_name": "Warehouse Supervisor",
                "complainant_email": "warehouse@supplier.com",
                "complainant_type": "distributor",
                "product_name": "Test Consumables Box",
                "product_code": "TCB-200",
                "product_lot_number": "LOT-2024-55555",
                "event_date": timezone.now().date() - timedelta(days=3),
                "event_description": "Outer box was crushed but contents verified intact",
                "event_location": "Distribution Center",
                "event_country": "United States",
                "category": "packaging",
                "severity": "minor",
                "priority": "low",
                "event_type": "other",
                "status": "closed",
                "assigned_to": admin,
                "target_closure_date": timezone.now().date() - timedelta(days=1),
            },
            {
                "title": "CMP-006: Documentation Clarity Issue",
                "description": "User manual section on maintenance procedures is ambiguous",
                "complainant_name": "Equipment Specialist",
                "complainant_email": "specialist@hospital.com",
                "complainant_type": "healthcare_provider",
                "product_name": "Glucose Analyzer X-2000",
                "product_code": "GA-2000-001",
                "product_lot_number": "LOT-2024-66666",
                "event_date": timezone.now().date() - timedelta(days=7),
                "event_description": "Maintenance section uses unclear terminology",
                "event_location": "Hospital Lab",
                "event_country": "United States",
                "category": "documentation",
                "severity": "minor",
                "priority": "medium",
                "event_type": "other",
                "status": "investigation_complete",
                "assigned_to": admin,
                "target_closure_date": timezone.now().date() + timedelta(days=21),
            },
        ]

        for complaint_spec in complaint_specs:
            defaults = {
                **complaint_spec,
                "created_by": admin,
                "updated_by": admin,
                "department": qa_dept,
            }

            _, is_new = Complaint.objects.get_or_create(
                title=complaint_spec["title"],
                defaults=defaults
            )
            if is_new:
                count += 1

        # Demo Change Controls - 4 change controls with various types and risk levels
        cc_specs = [
            {
                "title": "CC-001: SOP Update - Equipment Calibration Procedure",
                "description": "Update calibration frequency based on recent audit findings",
                "change_type": "document",
                "change_category": "major",
                "risk_level": "high",
                "current_stage": "screening",
                "department": qa_dept,
                "proposed_by": admin,
                "assigned_to": admin,
                "justification": "Audit findings indicate more frequent calibration required",
                "impact_summary": "Will require updated training and adjustment to maintenance schedule",
                "is_emergency": False,
                "target_completion_date": timezone.now() + timedelta(days=45),
            },
            {
                "title": "CC-002: Equipment Upgrade - New Analyzer Installation",
                "description": "Replace outdated analyzer with new model with enhanced features",
                "change_type": "equipment",
                "change_category": "major",
                "risk_level": "high",
                "current_stage": "impact_assessment",
                "department": manufacturing_dept,
                "proposed_by": admin,
                "assigned_to": admin,
                "justification": "Current equipment maintenance costs exceed replacement cost",
                "impact_summary": "Will require IQ/OQ/PQ and operator retraining",
                "is_emergency": False,
                "target_completion_date": timezone.now() + timedelta(days=90),
            },
            {
                "title": "CC-003: System Patch - Critical Security Update",
                "description": "Deploy critical security patches to LIMS system",
                "change_type": "software",
                "change_category": "minor",
                "risk_level": "medium",
                "current_stage": "approval",
                "department": Department.objects.filter(name="IT").first(),
                "proposed_by": admin,
                "assigned_to": admin,
                "justification": "Security vulnerability identified, vendor recommends immediate deployment",
                "impact_summary": "System may require brief downtime for patching",
                "is_emergency": False,
                "target_completion_date": timezone.now() + timedelta(days=14),
            },
            {
                "title": "CC-004: Process Validation - New Testing Method",
                "description": "Validate and implement new rapid testing methodology",
                "change_type": "process",
                "change_category": "major",
                "risk_level": "high",
                "current_stage": "implementation",
                "department": qa_control_dept,
                "proposed_by": admin,
                "assigned_to": admin,
                "justification": "New method can reduce testing time by 40% while maintaining accuracy",
                "impact_summary": "Requires protocol validation, training, and documentation updates",
                "is_emergency": False,
                "target_completion_date": timezone.now() + timedelta(days=60),
            },
        ]

        for cc_spec in cc_specs:
            defaults = {
                **cc_spec,
                "created_by": admin,
                "updated_by": admin,
            }

            _, is_new = ChangeControl.objects.get_or_create(
                title=cc_spec["title"],
                defaults=defaults
            )
            if is_new:
                count += 1

        return count
