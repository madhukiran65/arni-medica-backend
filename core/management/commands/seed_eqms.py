"""
Unified seed command for Arni Medica AI-EQMS.
Seeds: Workflows (with transitions + approval gates), InfoCard Types,
Job Functions, Departments, Roles, Sites, Product Lines, Users, Demo Data, and supporting entities.

Based on MasterControl reference architecture + Dot Compliance UI patterns.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import timedelta, datetime
from django.utils import timezone

from documents.models import DocumentInfocardType, Document
from training.models import JobFunction
from users.models import Department, Role, UserProfile, Site, ProductLine
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

        # 2. Roles (with granular permissions)
        role_count = self._seed_roles()
        self.stdout.write(self.style.SUCCESS(f"  Roles: {role_count} created"))

        # 3. Sites
        site_count = self._seed_sites()
        self.stdout.write(self.style.SUCCESS(f"  Sites: {site_count} created"))

        # 4. Product Lines
        product_count = self._seed_product_lines()
        self.stdout.write(self.style.SUCCESS(f"  Product Lines: {product_count} created"))

        # 5. InfoCard Types (MasterControl-style)
        type_count = self._seed_infocard_types()
        self.stdout.write(self.style.SUCCESS(f"  InfoCard Types: {type_count} created"))

        # 6. Workflows (comprehensive — from workflows/seed_data.py)
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

        # 7. Job Functions
        jf_count = self._seed_job_functions()
        self.stdout.write(self.style.SUCCESS(f"  Job Functions: {jf_count} created"))

        # 8. Admin user profile setup
        self._setup_admin_user()
        self.stdout.write(self.style.SUCCESS(f"  Admin User: Profile configured"))

        # 9. Create additional users
        user_count = self._seed_users()
        self.stdout.write(self.style.SUCCESS(f"  Users: {user_count} created"))

        # 10. User Profiles for remaining users
        profile_count = self._ensure_user_profiles()
        self.stdout.write(self.style.SUCCESS(f"  User Profiles: {profile_count} ensured"))

        # 11. Demo data
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
                "can_sign_documents": True, "can_release_documents": True,
                "can_obsolete_documents": True,
                "can_create_capa": True, "can_approve_capa": True,
                "can_close_capa": True,
                "can_create_complaints": True, "can_investigate_complaints": True,
                "can_create_deviations": True, "can_approve_deviations": True,
                "can_create_change_controls": True, "can_approve_change_controls": True,
                "can_log_training": True, "can_assign_training": True,
                "can_create_courses": True,
                "can_create_audit": True, "can_lead_audit": True,
                "can_manage_suppliers": True, "can_qualify_suppliers": True,
                "can_create_forms": True, "can_publish_forms": True,
                "can_view_audit_trail": True,
                "can_manage_users": True, "can_manage_settings": True,
                "can_manage_workflows": True, "can_export_data": True,
            },
            {
                "name": "QA Manager",
                "can_create_documents": True, "can_approve_documents": True,
                "can_sign_documents": True, "can_release_documents": True,
                "can_obsolete_documents": True,
                "can_create_capa": True, "can_approve_capa": True,
                "can_close_capa": True,
                "can_create_complaints": True, "can_investigate_complaints": True,
                "can_create_deviations": True, "can_approve_deviations": True,
                "can_create_change_controls": True, "can_approve_change_controls": True,
                "can_log_training": True, "can_assign_training": True,
                "can_create_courses": True,
                "can_create_audit": True, "can_lead_audit": True,
                "can_manage_suppliers": True, "can_qualify_suppliers": True,
                "can_create_forms": True, "can_publish_forms": True,
                "can_view_audit_trail": True,
                "can_manage_users": False, "can_manage_settings": False,
                "can_manage_workflows": True, "can_export_data": True,
            },
            {
                "name": "Document Controller",
                "can_create_documents": True, "can_approve_documents": True,
                "can_sign_documents": True, "can_release_documents": True,
                "can_obsolete_documents": True,
                "can_create_capa": False, "can_approve_capa": False,
                "can_close_capa": False,
                "can_create_complaints": False, "can_investigate_complaints": False,
                "can_create_deviations": False, "can_approve_deviations": False,
                "can_create_change_controls": False, "can_approve_change_controls": False,
                "can_log_training": False, "can_assign_training": False,
                "can_create_courses": False,
                "can_create_audit": False, "can_lead_audit": False,
                "can_manage_suppliers": False, "can_qualify_suppliers": False,
                "can_create_forms": True, "can_publish_forms": False,
                "can_view_audit_trail": True,
                "can_manage_users": False, "can_manage_settings": False,
                "can_manage_workflows": False, "can_export_data": True,
            },
            {
                "name": "Quality Engineer",
                "can_create_documents": True, "can_approve_documents": False,
                "can_sign_documents": False, "can_release_documents": False,
                "can_obsolete_documents": False,
                "can_create_capa": True, "can_approve_capa": False,
                "can_close_capa": False,
                "can_create_complaints": True, "can_investigate_complaints": True,
                "can_create_deviations": True, "can_approve_deviations": False,
                "can_create_change_controls": True, "can_approve_change_controls": False,
                "can_log_training": True, "can_assign_training": False,
                "can_create_courses": False,
                "can_create_audit": False, "can_lead_audit": False,
                "can_manage_suppliers": False, "can_qualify_suppliers": False,
                "can_create_forms": False, "can_publish_forms": False,
                "can_view_audit_trail": True,
                "can_manage_users": False, "can_manage_settings": False,
                "can_manage_workflows": False, "can_export_data": False,
            },
            {
                "name": "Training Coordinator",
                "can_create_documents": False, "can_approve_documents": False,
                "can_sign_documents": False, "can_create_capa": False,
                "can_close_capa": False, "can_create_complaints": False,
                "can_log_training": True, "can_create_audit": False,
                "can_view_audit_trail": False, "can_manage_users": False,
                "can_manage_settings": False, "can_create_deviations": False,
                "can_create_courses": True, "can_assign_training": True,
            },
            {
                "name": "Viewer",
                "can_create_documents": False, "can_approve_documents": False,
                "can_sign_documents": False, "can_create_capa": False,
                "can_close_capa": False, "can_create_complaints": False,
                "can_log_training": False, "can_create_audit": False,
                "can_view_audit_trail": True, "can_manage_users": False,
                "can_manage_settings": False, "can_create_deviations": False,
                "can_create_courses": False, "can_assign_training": False,
            },
        ]
        for role_data in roles:
            name = role_data.pop("name")
            role, is_new = Role.objects.get_or_create(
                name=name, defaults=role_data
            )
            if is_new:
                created += 1
            else:
                # Update existing roles with new permissions
                for key, value in role_data.items():
                    setattr(role, key, value)
                role.save()
        return created

    def _seed_sites(self):
        """Seed Arni Medica Diagnostics sites."""
        created = 0
        sites = [
            {
                "name": "Hyderabad HQ",
                "code": "HYD",
                "address": "Survey No. 42, Genome Valley, Shamirpet",
                "city": "Hyderabad",
                "state": "Telangana",
                "country": "India",
            },
            {
                "name": "Bengaluru R&D Center",
                "code": "BLR",
                "address": "IT Park, Whitefield",
                "city": "Bengaluru",
                "state": "Karnataka",
                "country": "India",
            },
            {
                "name": "Mumbai Manufacturing",
                "code": "MUM",
                "address": "MIDC Industrial Area, Andheri East",
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India",
            },
            {
                "name": "US Operations",
                "code": "US",
                "address": "100 Diagnostics Way, Suite 300",
                "city": "San Diego",
                "state": "California",
                "country": "United States",
            },
        ]
        for site_data in sites:
            _, is_new = Site.objects.get_or_create(
                code=site_data["code"],
                defaults=site_data
            )
            if is_new:
                created += 1
        return created

    def _seed_product_lines(self):
        """Seed Arni Medica product lines."""
        created = 0
        products = [
            {
                "name": "Glucose Analyzers",
                "code": "GA",
                "description": "Point-of-care glucose monitoring systems",
            },
            {
                "name": "Rapid Test Kits",
                "code": "RTK",
                "description": "Lateral flow immunoassay test kits",
            },
            {
                "name": "Quality Control Reagents",
                "code": "QCR",
                "description": "QC reagents for laboratory instruments",
            },
            {
                "name": "Hematology Instruments",
                "code": "HEM",
                "description": "Complete blood count analyzers",
            },
            {
                "name": "Clinical Chemistry",
                "code": "CCH",
                "description": "Automated clinical chemistry analyzers",
            },
        ]
        for product_data in products:
            _, is_new = ProductLine.objects.get_or_create(
                code=product_data["code"],
                defaults=product_data
            )
            if is_new:
                created += 1
        return created

    def _setup_admin_user(self):
        """Configure the existing admin user with profile, department, site, roles."""
        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            return

        qa_dept = Department.objects.filter(name="Quality Assurance").first()
        hyd_site = Site.objects.filter(code="HYD").first()
        admin_role = Role.objects.filter(name="Administrator").first()
        qa_director_jf = JobFunction.objects.filter(code="QAD").first()

        profile, _ = UserProfile.objects.update_or_create(
            user=admin,
            defaults={"employee_id": "EMP-0001"}
        )
        profile.department = qa_dept
        profile.site = hyd_site
        profile.title = "Quality Assurance Director"
        profile.phone = "+91-40-XXXX-XXXX"
        profile.date_of_joining = datetime(2020, 1, 15).date()
        if qa_director_jf:
            profile.job_function = qa_director_jf
        profile.save()

        # Add Administrator role via M2M on UserProfile
        if admin_role:
            profile.roles.add(admin_role)

    def _seed_users(self):
        """Create 15 additional users with profiles, departments, sites, and roles."""
        created = 0
        admin = User.objects.filter(is_superuser=True).first()

        # Clear auto-generated employee_ids (EMP-XXXX) that may conflict
        # These were created by _ensure_user_profiles() in prior runs
        reserved_ids = [f"EMP-{i:04d}" for i in range(2, 17)]  # EMP-0002 to EMP-0016
        conflicting = UserProfile.objects.filter(employee_id__in=reserved_ids)
        for p in conflicting:
            # Reassign to a non-conflicting temp id
            p.employee_id = f"AUTO-{p.user.pk:04d}"
            p.save()

        # Fetch departments, sites, roles, and job functions
        qa_dept = Department.objects.filter(name="Quality Assurance").first()
        qc_dept = Department.objects.filter(name="Quality Control").first()
        reg_dept = Department.objects.filter(name="Regulatory Affairs").first()
        mfg_dept = Department.objects.filter(name="Manufacturing").first()
        rd_dept = Department.objects.filter(name="Research & Development").first()
        hr_dept = Department.objects.filter(name="Human Resources").first()
        it_dept = Department.objects.filter(name="IT").first()
        clinical_dept = Department.objects.filter(name="Clinical Affairs").first()
        supply_dept = Department.objects.filter(name="Supply Chain").first()

        hyd_site = Site.objects.filter(code="HYD").first()
        blr_site = Site.objects.filter(code="BLR").first()
        mum_site = Site.objects.filter(code="MUM").first()
        us_site = Site.objects.filter(code="US").first()

        admin_role = Role.objects.filter(name="Administrator").first()
        qa_mgr_role = Role.objects.filter(name="QA Manager").first()
        doc_ctrl_role = Role.objects.filter(name="Document Controller").first()
        qual_eng_role = Role.objects.filter(name="Quality Engineer").first()
        train_coord_role = Role.objects.filter(name="Training Coordinator").first()

        qm_jf = JobFunction.objects.filter(code="QM").first()
        qe_jf = JobFunction.objects.filter(code="QE").first()
        dc_jf = JobFunction.objects.filter(code="DC").first()
        ra_jf = JobFunction.objects.filter(code="RA").first()
        qad_jf = JobFunction.objects.filter(code="QAD").first()
        ia_jf = JobFunction.objects.filter(code="IA").first()
        tc_jf = JobFunction.objects.filter(code="TC").first()
        mfg_jf = JobFunction.objects.filter(code="MFG").first()

        users_data = [
            {
                "username": "priya.sharma",
                "email": "priya.sharma@arnimedica.com",
                "first_name": "Priya",
                "last_name": "Sharma",
                "employee_id": "EMP-0002",
                "title": "QA Director",
                "phone": "+91-40-1234-5001",
                "department": qa_dept,
                "site": hyd_site,
                "roles": [admin_role, qa_mgr_role],
                "job_function": qad_jf,
                "supervisor": admin,
                "date_of_joining": datetime(2019, 6, 1).date(),
            },
            {
                "username": "rajesh.kumar",
                "email": "rajesh.kumar@arnimedica.com",
                "first_name": "Rajesh",
                "last_name": "Kumar",
                "employee_id": "EMP-0003",
                "title": "QA Manager",
                "phone": "+91-40-1234-5002",
                "department": qa_dept,
                "site": hyd_site,
                "roles": [qa_mgr_role],
                "job_function": qm_jf,
                "supervisor": admin,
                "date_of_joining": datetime(2020, 3, 15).date(),
            },
            {
                "username": "anita.reddy",
                "email": "anita.reddy@arnimedica.com",
                "first_name": "Anita",
                "last_name": "Reddy",
                "employee_id": "EMP-0004",
                "title": "Document Controller",
                "phone": "+91-40-1234-5003",
                "department": qa_dept,
                "site": hyd_site,
                "roles": [doc_ctrl_role],
                "job_function": dc_jf,
                "supervisor": admin,
                "date_of_joining": datetime(2021, 1, 10).date(),
            },
            {
                "username": "venkat.rao",
                "email": "venkat.rao@arnimedica.com",
                "first_name": "Venkat",
                "last_name": "Rao",
                "employee_id": "EMP-0005",
                "title": "Quality Engineer",
                "phone": "+91-22-1234-5004",
                "department": qc_dept,
                "site": mum_site,
                "roles": [qual_eng_role],
                "job_function": qe_jf,
                "supervisor": admin,
                "date_of_joining": datetime(2021, 7, 20).date(),
            },
            {
                "username": "deepika.nair",
                "email": "deepika.nair@arnimedica.com",
                "first_name": "Deepika",
                "last_name": "Nair",
                "employee_id": "EMP-0006",
                "title": "Regulatory Affairs Manager",
                "phone": "+1-619-1234-5005",
                "department": reg_dept,
                "site": us_site,
                "roles": [qa_mgr_role],
                "job_function": ra_jf,
                "supervisor": admin,
                "date_of_joining": datetime(2019, 9, 5).date(),
            },
            {
                "username": "suresh.patel",
                "email": "suresh.patel@arnimedica.com",
                "first_name": "Suresh",
                "last_name": "Patel",
                "employee_id": "EMP-0007",
                "title": "Manufacturing Head",
                "phone": "+91-22-1234-5006",
                "department": mfg_dept,
                "site": mum_site,
                "roles": [qa_mgr_role],
                "job_function": mfg_jf,
                "supervisor": admin,
                "date_of_joining": datetime(2018, 5, 12).date(),
            },
            {
                "username": "kavitha.menon",
                "email": "kavitha.menon@arnimedica.com",
                "first_name": "Kavitha",
                "last_name": "Menon",
                "employee_id": "EMP-0008",
                "title": "R&D Director",
                "phone": "+91-80-1234-5007",
                "department": rd_dept,
                "site": blr_site,
                "roles": [admin_role],
                "job_function": qad_jf,
                "supervisor": admin,
                "date_of_joining": datetime(2017, 8, 22).date(),
            },
            {
                "username": "arun.joshi",
                "email": "arun.joshi@arnimedica.com",
                "first_name": "Arun",
                "last_name": "Joshi",
                "employee_id": "EMP-0009",
                "title": "Training Coordinator",
                "phone": "+91-40-1234-5008",
                "department": hr_dept,
                "site": hyd_site,
                "roles": [train_coord_role],
                "job_function": tc_jf,
                "supervisor": admin,
                "date_of_joining": datetime(2021, 11, 1).date(),
            },
            {
                "username": "meena.gupta",
                "email": "meena.gupta@arnimedica.com",
                "first_name": "Meena",
                "last_name": "Gupta",
                "employee_id": "EMP-0010",
                "title": "QC Lab Supervisor",
                "phone": "+91-22-1234-5009",
                "department": qc_dept,
                "site": mum_site,
                "roles": [qual_eng_role],
                "job_function": qe_jf,
                "supervisor": admin,
                "date_of_joining": datetime(2020, 4, 18).date(),
            },
            {
                "username": "sanjay.desai",
                "email": "sanjay.desai@arnimedica.com",
                "first_name": "Sanjay",
                "last_name": "Desai",
                "employee_id": "EMP-0011",
                "title": "IT Manager",
                "phone": "+91-40-1234-5010",
                "department": it_dept,
                "site": hyd_site,
                "roles": [admin_role],
                "job_function": qm_jf,
                "supervisor": admin,
                "date_of_joining": datetime(2019, 2, 10).date(),
            },
            {
                "username": "lakshmi.iyer",
                "email": "lakshmi.iyer@arnimedica.com",
                "first_name": "Lakshmi",
                "last_name": "Iyer",
                "employee_id": "EMP-0012",
                "title": "Clinical Affairs Lead",
                "phone": "+1-619-1234-5011",
                "department": clinical_dept,
                "site": us_site,
                "roles": [qual_eng_role],
                "job_function": qe_jf,
                "supervisor": admin,
                "date_of_joining": datetime(2020, 8, 3).date(),
            },
            {
                "username": "ravi.krishnan",
                "email": "ravi.krishnan@arnimedica.com",
                "first_name": "Ravi",
                "last_name": "Krishnan",
                "employee_id": "EMP-0013",
                "title": "Supply Chain Manager",
                "phone": "+91-22-1234-5012",
                "department": supply_dept,
                "site": mum_site,
                "roles": [qa_mgr_role],
                "job_function": qm_jf,
                "supervisor": admin,
                "date_of_joining": datetime(2019, 10, 28).date(),
            },
            {
                "username": "pooja.verma",
                "email": "pooja.verma@arnimedica.com",
                "first_name": "Pooja",
                "last_name": "Verma",
                "employee_id": "EMP-0014",
                "title": "Quality Engineer",
                "phone": "+91-80-1234-5013",
                "department": qa_dept,
                "site": blr_site,
                "roles": [qual_eng_role],
                "job_function": qe_jf,
                "supervisor": admin,
                "date_of_joining": datetime(2021, 5, 24).date(),
            },
            {
                "username": "amit.singh",
                "email": "amit.singh@arnimedica.com",
                "first_name": "Amit",
                "last_name": "Singh",
                "employee_id": "EMP-0015",
                "title": "Internal Auditor",
                "phone": "+91-40-1234-5014",
                "department": qa_dept,
                "site": hyd_site,
                "roles": [qa_mgr_role],
                "job_function": ia_jf,
                "supervisor": admin,
                "date_of_joining": datetime(2020, 12, 7).date(),
            },
            {
                "username": "sneha.bhat",
                "email": "sneha.bhat@arnimedica.com",
                "first_name": "Sneha",
                "last_name": "Bhat",
                "employee_id": "EMP-0016",
                "title": "Regulatory Specialist",
                "phone": "+91-40-1234-5015",
                "department": reg_dept,
                "site": hyd_site,
                "roles": [qual_eng_role],
                "job_function": qe_jf,
                "supervisor": admin,
                "date_of_joining": datetime(2021, 3, 15).date(),
            },
        ]

        for user_data in users_data:
            roles_list = user_data.pop("roles")
            job_function = user_data.pop("job_function")
            supervisor = user_data.pop("supervisor")
            email = user_data["email"]
            password = email.split("@")[0] + "123"  # Default password

            user, is_new = User.objects.get_or_create(
                username=user_data["username"],
                defaults={
                    "email": email,
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                }
            )

            if is_new:
                user.set_password(password)
                user.save()
                created += 1

            # Create or update UserProfile
            defaults = {
                "employee_id": user_data["employee_id"],
                "department": user_data["department"],
                "site": user_data["site"],
                "title": user_data["title"],
                "phone": user_data["phone"],
                "date_of_joining": user_data["date_of_joining"],
            }
            if job_function:
                defaults["job_function"] = job_function
            if supervisor:
                defaults["supervisor"] = supervisor
            profile, _ = UserProfile.objects.update_or_create(
                user=user,
                defaults=defaults
            )

            # Assign roles via M2M on UserProfile (not user.groups)
            profile.roles.clear()
            for role in roles_list:
                if role:
                    profile.roles.add(role)

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

        # Demo Documents - 20 documents with descriptions, owners, and varied states
        doc_specs = [
            {
                "title": "SOP-001: Equipment Calibration Procedure",
                "prefix": "SOP",
                "vault_state": "released",
                "department": qa_dept,
                "requires_training": True,
                "review_period_months": 24,
                "description": "Standard operating procedure for calibrating all laboratory instruments including glucose analyzers, hematology counters, and pipettes. Covers calibration intervals, reference standards, acceptance criteria, and out-of-tolerance handling per ISO 13485:2016 Section 7.6.",
                "regulatory_requirement": "ISO 13485:2016 Sec 7.6",
                "confidentiality_level": "internal",
            },
            {
                "title": "WI-001: Blood Sample Collection Guide",
                "prefix": "WI",
                "vault_state": "released",
                "department": manufacturing_dept,
                "requires_training": True,
                "review_period_months": 12,
                "description": "Step-by-step work instruction for proper venipuncture and capillary blood sample collection. Includes patient preparation, specimen labeling requirements, order of draw, and sample handling/transport specifications.",
                "regulatory_requirement": "CLSI H3-A6",
            },
            {
                "title": "FRM-001: Batch Record Template",
                "prefix": "FRM",
                "vault_state": "released",
                "department": manufacturing_dept,
                "requires_training": False,
                "review_period_months": 36,
                "description": "Master batch record template for documenting manufacturing steps, in-process checks, environmental conditions, and equipment used during production of IVD reagent kits. Includes spaces for operator signatures and QC verification.",
            },
            {
                "title": "POL-001: Quality Policy Manual",
                "prefix": "POL",
                "vault_state": "released",
                "department": qa_dept,
                "requires_training": True,
                "review_period_months": 24,
                "description": "Top-level quality policy document defining Arni Medica's commitment to quality, regulatory compliance, and continuous improvement. Establishes the quality management system scope, organizational responsibilities, and quality objectives aligned with ISO 13485 and FDA 21 CFR 820.",
                "regulatory_requirement": "ISO 13485:2016 Sec 4.2.2",
                "confidentiality_level": "internal",
            },
            {
                "title": "VAL-001: IQ/OQ/PQ Protocol for Glucose Analyzer",
                "prefix": "VAL",
                "vault_state": "draft",
                "department": rd_dept,
                "requires_training": False,
                "review_period_months": 60,
                "description": "Installation, Operational, and Performance Qualification protocol for the new X-3000 Glucose Analyzer. Covers system verification, functional testing against specifications, and performance validation using certified reference materials.",
                "regulatory_requirement": "FDA 21 CFR 820.75",
            },
            {
                "title": "SPE-001: Reagent Raw Material Specifications",
                "prefix": "SPE",
                "vault_state": "released",
                "department": manufacturing_dept,
                "requires_training": False,
                "review_period_months": 36,
                "description": "Defines acceptance specifications for all incoming raw materials used in reagent manufacturing. Covers purity requirements, stability criteria, supplier qualification standards, and incoming inspection test methods.",
            },
            {
                "title": "PRO-001: Method Validation Protocol",
                "prefix": "PRO",
                "vault_state": "released",
                "department": qa_control_dept,
                "requires_training": False,
                "review_period_months": 48,
                "description": "Protocol for validating analytical test methods including accuracy, precision, linearity, range, specificity, detection limits, and robustness in accordance with ICH Q2(R1) guidelines.",
                "regulatory_requirement": "ICH Q2(R1)",
            },
            {
                "title": "CHK-001: Equipment Maintenance Checklist",
                "prefix": "CHK",
                "vault_state": "archived",
                "department": manufacturing_dept,
                "requires_training": False,
                "review_period_months": 12,
                "description": "Daily and weekly preventive maintenance checklist for production line equipment. Superseded by CHK-002 which includes additional environmental monitoring checks.",
            },
            {
                "title": "REG-001: FDA 510(k) Submission Compliance Matrix",
                "prefix": "REG",
                "vault_state": "released",
                "department": regulatory_dept,
                "requires_training": False,
                "review_period_months": 24,
                "description": "Compliance matrix mapping FDA 510(k) submission requirements to Arni Medica's quality system documents. Tracks predicate device comparisons, substantial equivalence arguments, and performance data requirements.",
                "regulatory_requirement": "FDA 21 CFR 807 Subpart E",
                "confidentiality_level": "confidential",
            },
            {
                "title": "TRN-001: Annual Operator Training Material",
                "prefix": "TRN",
                "vault_state": "released",
                "department": qa_dept,
                "requires_training": True,
                "review_period_months": 12,
                "description": "Comprehensive training curriculum for production operators covering GMP principles, equipment operation, documentation practices, and safety protocols. Includes knowledge assessment questions and competency evaluation criteria.",
            },
            {
                "title": "SOP-002: Document Control Procedure",
                "prefix": "SOP",
                "vault_state": "released",
                "department": qa_dept,
                "requires_training": True,
                "review_period_months": 24,
                "description": "Defines the process for creating, reviewing, approving, distributing, and retiring controlled documents within the quality management system. Covers document numbering, revision control, electronic signatures, and periodic review requirements.",
                "regulatory_requirement": "ISO 13485:2016 Sec 4.2.4",
            },
            {
                "title": "SOP-003: CAPA Management Procedure",
                "prefix": "SOP",
                "vault_state": "released",
                "department": qa_dept,
                "requires_training": True,
                "review_period_months": 24,
                "description": "Standard procedure for identifying, documenting, investigating, and resolving corrective and preventive actions. Includes root cause analysis methodologies, effectiveness verification criteria, and escalation procedures for critical CAPAs.",
                "regulatory_requirement": "FDA 21 CFR 820.90",
            },
            {
                "title": "SOP-004: Complaint Handling Procedure",
                "prefix": "SOP",
                "vault_state": "released",
                "department": qa_dept,
                "requires_training": True,
                "review_period_months": 12,
                "description": "Procedure for receiving, evaluating, investigating, and resolving customer complaints. Includes MDR reportability assessment criteria, trending analysis requirements, and FDA/MedWatch reporting timelines.",
                "regulatory_requirement": "FDA 21 CFR 820.198",
            },
            {
                "title": "MAN-001: Design History File Index",
                "prefix": "MAN",
                "vault_state": "released",
                "department": rd_dept,
                "requires_training": False,
                "review_period_months": 36,
                "description": "Master index and organization guide for the Design History File (DHF) of the Glucose Analyzer product family. References all design inputs, outputs, reviews, verification, and validation records.",
                "regulatory_requirement": "FDA 21 CFR 820.30",
                "confidentiality_level": "confidential",
            },
            {
                "title": "PLN-001: Annual Quality Plan 2025",
                "prefix": "PLN",
                "vault_state": "released",
                "department": qa_dept,
                "requires_training": False,
                "review_period_months": 12,
                "description": "Annual quality objectives, KPIs, internal audit schedule, management review plan, and continuous improvement initiatives for fiscal year 2025. Defines measurable targets for CAPA closure rates, complaint response times, and training compliance.",
            },
            {
                "title": "GUD-001: Risk Management Guidelines",
                "prefix": "GUD",
                "vault_state": "released",
                "department": qa_dept,
                "requires_training": True,
                "review_period_months": 24,
                "description": "Guidelines for applying ISO 14971 risk management processes throughout the product lifecycle. Covers hazard identification, risk estimation, risk evaluation, risk control measures, and residual risk acceptability criteria.",
                "regulatory_requirement": "ISO 14971:2019",
            },
            {
                "title": "DRW-001: Rapid Test Kit Assembly Drawing",
                "prefix": "DRW",
                "vault_state": "released",
                "department": manufacturing_dept,
                "requires_training": False,
                "review_period_months": 36,
                "description": "Engineering assembly drawing for the Lateral Flow Rapid Test Kit showing component layout, membrane placement, conjugate pad positioning, and housing assembly specifications with dimensional tolerances.",
                "confidentiality_level": "confidential",
            },
            {
                "title": "LOG-001: Environmental Monitoring Log",
                "prefix": "LOG",
                "vault_state": "draft",
                "department": manufacturing_dept,
                "requires_training": False,
                "review_period_months": 12,
                "description": "Daily log template for recording cleanroom environmental conditions including temperature, humidity, particulate counts, and differential pressure readings across manufacturing zones.",
            },
            {
                "title": "RPT-001: Annual Product Quality Review",
                "prefix": "RPT",
                "vault_state": "draft",
                "department": qa_dept,
                "requires_training": False,
                "review_period_months": 12,
                "description": "Template and guidance for conducting the Annual Product Quality Review (APQR) covering batch analysis trends, deviation summaries, CAPA effectiveness, stability data review, and process capability assessments.",
            },
            {
                "title": "LBL-001: Product Labeling Requirements",
                "prefix": "LBL",
                "vault_state": "released",
                "department": regulatory_dept,
                "requires_training": True,
                "review_period_months": 24,
                "description": "Specification document defining labeling requirements for all IVD products including UDI compliance, IFU content requirements, symbol standards (ISO 15223-1), and country-specific regulatory labeling mandates.",
                "regulatory_requirement": "FDA 21 CFR 809.10",
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
