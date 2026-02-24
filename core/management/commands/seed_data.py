"""
Seed data for Arni Medica AI-EQMS
Creates default departments, roles, and superuser
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import Department, Role, UserProfile


class Command(BaseCommand):
    help = 'Seed initial data: departments, roles, and admin user'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Arni Medica EQMS data...\n')

        # --- Departments ---
        dept_names = [
            ('Quality Assurance', 'Quality Assurance & Control'),
            ('Regulatory Affairs', 'Regulatory Compliance & Submissions'),
            ('Research & Development', 'Product Development & Innovation'),
            ('Manufacturing', 'Production & Manufacturing Operations'),
            ('Supply Chain', 'Procurement & Supply Chain Management'),
            ('Clinical Affairs', 'Clinical Trials & Studies'),
            ('Management', 'Executive Management'),
        ]
        departments = {}
        for name, desc in dept_names:
            dept, created = Department.objects.get_or_create(
                name=name,
                defaults={'description': desc}
            )
            departments[name] = dept
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  Department: {dept.name} [{status}]')

        # --- Roles ---
        roles_data = [
            {
                'name': 'Quality Director',
                'description': 'Head of Quality — full system access',
                'can_create_documents': True,
                'can_approve_documents': True,
                'can_sign_documents': True,
                'can_create_capa': True,
                'can_close_capa': True,
                'can_create_complaints': True,
                'can_log_training': True,
                'can_create_audit': True,
                'can_view_audit_trail': True,
                'can_manage_users': True,
            },
            {
                'name': 'QA Manager',
                'description': 'Quality Assurance Manager',
                'can_create_documents': True,
                'can_approve_documents': True,
                'can_sign_documents': True,
                'can_create_capa': True,
                'can_close_capa': True,
                'can_create_complaints': True,
                'can_log_training': True,
                'can_create_audit': True,
                'can_view_audit_trail': True,
                'can_manage_users': False,
            },
            {
                'name': 'Regulatory Specialist',
                'description': 'Regulatory Affairs Specialist',
                'can_create_documents': True,
                'can_approve_documents': True,
                'can_sign_documents': True,
                'can_create_capa': True,
                'can_close_capa': False,
                'can_create_complaints': True,
                'can_log_training': False,
                'can_create_audit': False,
                'can_view_audit_trail': True,
                'can_manage_users': False,
            },
            {
                'name': 'R&D Engineer',
                'description': 'Research & Development Engineer',
                'can_create_documents': True,
                'can_approve_documents': False,
                'can_sign_documents': True,
                'can_create_capa': True,
                'can_close_capa': False,
                'can_create_complaints': False,
                'can_log_training': False,
                'can_create_audit': False,
                'can_view_audit_trail': False,
                'can_manage_users': False,
            },
            {
                'name': 'Manufacturing Lead',
                'description': 'Manufacturing Team Lead',
                'can_create_documents': False,
                'can_approve_documents': False,
                'can_sign_documents': True,
                'can_create_capa': True,
                'can_close_capa': False,
                'can_create_complaints': True,
                'can_log_training': False,
                'can_create_audit': False,
                'can_view_audit_trail': False,
                'can_manage_users': False,
            },
            {
                'name': 'Auditor',
                'description': 'Internal/External Auditor',
                'can_create_documents': False,
                'can_approve_documents': False,
                'can_sign_documents': False,
                'can_create_capa': True,
                'can_close_capa': False,
                'can_create_complaints': False,
                'can_log_training': False,
                'can_create_audit': True,
                'can_view_audit_trail': True,
                'can_manage_users': False,
            },
            {
                'name': 'Viewer',
                'description': 'Read-only access to EQMS',
                'can_create_documents': False,
                'can_approve_documents': False,
                'can_sign_documents': False,
                'can_create_capa': False,
                'can_close_capa': False,
                'can_create_complaints': False,
                'can_log_training': False,
                'can_create_audit': False,
                'can_view_audit_trail': False,
                'can_manage_users': False,
            },
        ]
        roles = {}
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults=role_data
            )
            roles[role_data['name']] = role
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  Role: {role.name} [{status}]')

        # --- Superuser: MK Parvathaneni ---
        admin_username = 'mkp'
        admin_email = 'mkparvathaneni6@gmail.com'
        if not User.objects.filter(username=admin_username).exists():
            admin_user = User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password='ArniMedica2026!',
                first_name='MK',
                last_name='Parvathaneni',
            )
            profile = UserProfile.objects.create(
                user=admin_user,
                department=departments['Quality Assurance'],
                employee_id='AM-001',
            )
            profile.roles.add(roles['Quality Director'])
            self.stdout.write(self.style.SUCCESS(
                f'\n  Superuser created: {admin_username} / ArniMedica2026!'
            ))
        else:
            self.stdout.write(f'  Superuser {admin_username} already exists')

        self.stdout.write(self.style.SUCCESS('\nSeed data complete!'))
