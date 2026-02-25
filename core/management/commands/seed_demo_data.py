"""
Django management command to seed demo data for Arni Medica eQMS backend.
Creates realistic pharmaceutical IVD demo data across all main modules.

Usage:
    python manage.py seed_demo_data

Safe to run multiple times - uses get_or_create to avoid duplicates.
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, datetime
import random

from capa.models import CAPA
from complaints.models import Complaint
from deviations.models import Deviation
from documents.models import Document, DocumentInfocardType, DocumentSubType
from training.models import TrainingCourse, TrainingAssignment, JobFunction
from suppliers.models import Supplier
from change_controls.models import ChangeControl
from audit_mgmt.models import AuditPlan, AuditFinding
from users.models import Department


class Command(BaseCommand):
    help = 'Seed demo data for Arni Medica eQMS backend'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing demo data before seeding',
        )

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS('Starting demo data seeding...'))

            # Get or create admin user
            admin_user, _ = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@arnimedica.com',
                    'first_name': 'Admin',
                    'last_name': 'User',
                    'is_staff': True,
                    'is_superuser': True,
                }
            )
            self.stdout.write(f"Using admin user: {admin_user.username}")

            # Get or create QA department
            qa_dept, _ = Department.objects.get_or_create(
                name='Quality Assurance',
                defaults={'description': 'Quality Assurance Department'}
            )
            manufacturing_dept, _ = Department.objects.get_or_create(
                name='Manufacturing',
                defaults={'description': 'Manufacturing Department'}
            )
            regulatory_dept, _ = Department.objects.get_or_create(
                name='Regulatory Affairs',
                defaults={'description': 'Regulatory Affairs Department'}
            )
            self.stdout.write(self.style.SUCCESS(f'Created departments'))

            # Seed each module
            self.seed_capa(admin_user, qa_dept)
            self.seed_complaints(admin_user, qa_dept)
            self.seed_deviations(admin_user, manufacturing_dept)
            self.seed_documents(admin_user, qa_dept)
            self.seed_training(admin_user, qa_dept)
            self.seed_suppliers(admin_user, qa_dept)
            self.seed_change_controls(admin_user, manufacturing_dept)
            self.seed_audits(admin_user, qa_dept)

            self.stdout.write(self.style.SUCCESS('Demo data seeded successfully!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error seeding demo data: {str(e)}'))
            raise CommandError(str(e))

    def seed_capa(self, user, department):
        """Seed CAPA records with realistic pharmaceutical data"""
        self.stdout.write('Seeding CAPA data...')

        capa_data = [
            {
                'capa_id': 'CAPA-2025-001',
                'title': 'Reagent Stability Failure in Lot #RB2024001',
                'description': 'Reagent bottle failed stability testing at 6-month mark',
                'source': 'complaint',
                'category': 'product',
                'priority': 'critical',
                'capa_type': 'corrective',
                'current_phase': 'investigation',
                'what_happened': 'Reagent lot #RB2024001 showed degradation beyond specifications',
                'when_happened': timezone.now() - timedelta(days=15),
                'where_happened': 'Central QA Laboratory, Building A',
                'who_affected': 'Quality Control Team, Manufacturing Operations',
                'why_happened': 'Storage temperature exceeded specification (+2°C above max)',
                'how_discovered': 'Routine stability testing protocol',
                'risk_severity': 5,
                'risk_occurrence': 3,
                'risk_detection': 2,
            },
            {
                'capa_id': 'CAPA-2025-002',
                'title': 'False Positive Rate Exceeds Threshold',
                'description': 'IVD test kit showing elevated false positive results',
                'source': 'audit',
                'category': 'process',
                'priority': 'high',
                'capa_type': 'corrective',
                'current_phase': 'root_cause',
                'what_happened': 'False positive rate increased to 2.5% vs spec of <1%',
                'when_happened': timezone.now() - timedelta(days=10),
                'where_happened': 'Clinical Labs, Hospital Partners',
                'who_affected': 'End users, patients',
                'why_happened': 'Potential antibody binding issue in reagent formulation',
                'how_discovered': 'Customer complaint and field data analysis',
                'risk_severity': 5,
                'risk_occurrence': 4,
                'risk_detection': 4,
            },
            {
                'capa_id': 'CAPA-2025-003',
                'title': 'Documentation Gap in SOPs',
                'description': 'Missing critical steps in manufacturing SOP revision',
                'source': 'internal_observation',
                'category': 'documentation',
                'priority': 'medium',
                'capa_type': 'preventive',
                'current_phase': 'capa_plan',
                'what_happened': 'SOP-MFG-012 revision 2 missing validation steps',
                'when_happened': timezone.now() - timedelta(days=5),
                'where_happened': 'Manufacturing Operations',
                'who_affected': 'Manufacturing personnel, Quality Assurance',
                'why_happened': 'Incomplete document review before release',
                'how_discovered': 'Internal audit finding',
                'risk_severity': 3,
                'risk_occurrence': 2,
                'risk_detection': 3,
            },
            {
                'capa_id': 'CAPA-2025-004',
                'title': 'Equipment Calibration Drift',
                'description': 'pH meter showing calibration drift beyond limits',
                'source': 'management_review',
                'category': 'equipment',
                'priority': 'high',
                'capa_type': 'corrective',
                'current_phase': 'implementation',
                'what_happened': 'pH meter Cal-1500 drift exceeded ±0.2 units',
                'when_happened': timezone.now() - timedelta(days=8),
                'where_happened': 'Lab Building, Room 304',
                'who_affected': 'Lab technicians, QC operations',
                'why_happened': 'Extended use without recalibration, electrode degradation',
                'how_discovered': 'Monthly calibration verification',
                'risk_severity': 4,
                'risk_occurrence': 2,
                'risk_detection': 2,
            },
            {
                'capa_id': 'CAPA-2025-005',
                'title': 'Supplier Material Non-Conformance',
                'description': 'Incoming raw material failed purity specification',
                'source': 'supplier',
                'category': 'supplier',
                'priority': 'critical',
                'capa_type': 'both',
                'current_phase': 'effectiveness',
                'what_happened': 'Lot #SM2024156 tested at 98.2% purity vs spec 99.5%',
                'when_happened': timezone.now() - timedelta(days=20),
                'where_happened': 'Receiving Inspection Area',
                'who_affected': 'Manufacturing queue, Production schedule',
                'why_happened': 'Supplier process change not communicated',
                'how_discovered': 'Incoming quality inspection',
                'risk_severity': 5,
                'risk_occurrence': 2,
                'risk_detection': 1,
            },
            {
                'capa_id': 'CAPA-2025-006',
                'title': 'Training Compliance Gap',
                'description': 'Personnel not trained on new procedure before implementation',
                'source': 'inspection',
                'category': 'training',
                'priority': 'medium',
                'capa_type': 'preventive',
                'current_phase': 'investigation',
                'what_happened': '3 manufacturing staff assigned to new process without training',
                'when_happened': timezone.now() - timedelta(days=3),
                'where_happened': 'Manufacturing Floor, Line C',
                'who_affected': 'Manufacturing team, Quality Assurance',
                'why_happened': 'Inadequate training schedule coordination',
                'how_discovered': 'Manager observation',
                'risk_severity': 4,
                'risk_occurrence': 3,
                'risk_detection': 3,
            },
            {
                'capa_id': 'CAPA-2025-007',
                'title': 'System Validation Deficiency',
                'description': 'LIMS installation missing required validation protocols',
                'source': 'regulatory',
                'category': 'system',
                'priority': 'critical',
                'capa_type': 'corrective',
                'current_phase': 'root_cause',
                'what_happened': 'LIMS system deployed without complete IQ/OQ protocols',
                'when_happened': timezone.now() - timedelta(days=12),
                'where_happened': 'IT Department, Lab Operations',
                'who_affected': 'All lab operations, data integrity',
                'why_happened': 'Accelerated deployment timeline compressed validation',
                'how_discovered': 'Regulatory readiness assessment',
                'risk_severity': 5,
                'risk_occurrence': 2,
                'risk_detection': 2,
            },
            {
                'capa_id': 'CAPA-2025-008',
                'title': 'Sterility Test Failure - Media Fill',
                'description': 'Media fill test detected microbial contamination',
                'source': 'deviation',
                'category': 'process',
                'priority': 'critical',
                'capa_type': 'corrective',
                'current_phase': 'capa_plan',
                'what_happened': 'Media fill batch MF-2024-45 contaminated in 2/20 runs',
                'when_happened': timezone.now() - timedelta(days=7),
                'where_happened': 'Filling Line A, Class A Room',
                'who_affected': 'All products filled on Line A, patient safety',
                'why_happened': 'HEPA filter integrity compromised, aseptic technique deviation',
                'how_discovered': 'Routine media fill validation',
                'risk_severity': 5,
                'risk_occurrence': 2,
                'risk_detection': 2,
            },
            {
                'capa_id': 'CAPA-2025-009',
                'title': 'Label Printing Error Correction',
                'description': 'Labels printed with incorrect lot number prefix',
                'source': 'customer_feedback',
                'category': 'product',
                'priority': 'medium',
                'capa_type': 'corrective',
                'current_phase': 'closure',
                'what_happened': '500 units labeled with OLD lot prefix instead of NEW',
                'when_happened': timezone.now() - timedelta(days=25),
                'where_happened': 'Labeling Operations',
                'who_affected': 'Product shipment, customer receiving',
                'why_happened': 'Outdated label template not replaced in printer system',
                'how_discovered': 'Customer notification upon receipt',
                'risk_severity': 3,
                'risk_occurrence': 2,
                'risk_detection': 4,
            },
        ]

        for data in capa_data:
            try:
                capa, created = CAPA.objects.get_or_create(
                    capa_id=data['capa_id'],
                    defaults={
                        'title': data['title'],
                        'description': data['description'],
                        'source': data['source'],
                        'category': data['category'],
                        'priority': data['priority'],
                        'capa_type': data['capa_type'],
                        'current_phase': data['current_phase'],
                        'what_happened': data['what_happened'],
                        'when_happened': data['when_happened'],
                        'where_happened': data['where_happened'],
                        'who_affected': data['who_affected'],
                        'why_happened': data['why_happened'],
                        'how_discovered': data['how_discovered'],
                        'risk_severity': data['risk_severity'],
                        'risk_occurrence': data['risk_occurrence'],
                        'risk_detection': data['risk_detection'],
                        'assigned_to': user,
                        'department': department,
                        'created_by': user,
                        'updated_by': user,
                    }
                )
                if created:
                    self.stdout.write(f"  Created: {capa.capa_id}")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  Skipped {data['capa_id']}: {str(e)}"))

    def seed_complaints(self, user, department):
        """Seed Complaint records"""
        self.stdout.write('Seeding Complaint data...')

        complaint_data = [
            {
                'complaint_id': 'CMP-2025-001',
                'title': 'Device Not Functioning Properly',
                'description': 'IVD analyzer not processing samples correctly',
                'complainant_name': 'Dr. Sarah Johnson',
                'complainant_email': 'sjohnson@hospital.com',
                'complainant_type': 'healthcare_provider',
                'product_name': 'DiagnoSmart IVD-500',
                'product_code': 'DSM-500-001',
                'product_lot_number': 'LOT2024-001',
                'category': 'product_performance',
                'severity': 'critical',
                'priority': 'high',
                'event_description': 'Device displays error after 50 samples',
                'event_location': 'Central Lab, Hospital XYZ',
                'event_country': 'United States',
                'event_type': 'malfunction',
                'is_reportable_to_fda': True,
            },
            {
                'complaint_id': 'CMP-2025-002',
                'title': 'Reagent Instability Issues',
                'description': 'Reagent shows color change before expiration',
                'complainant_name': 'Quality Manager',
                'complainant_email': 'qm@labcorp.com',
                'complainant_type': 'healthcare_provider',
                'product_name': 'ReagentPlex Plus',
                'product_code': 'RPL-001-002',
                'product_lot_number': 'LOT2024-045',
                'category': 'product_quality',
                'severity': 'major',
                'priority': 'high',
                'event_description': 'Reagent degradation observed at 3 months',
                'event_location': 'Quest Diagnostics Facility',
                'event_country': 'United States',
                'event_type': 'other',
                'is_reportable_to_fda': False,
            },
            {
                'complaint_id': 'CMP-2025-003',
                'title': 'Labeling Information Unclear',
                'description': 'Instructions for use difficult to understand',
                'complainant_name': 'John Smith',
                'complainant_email': 'jsmith@clinic.org',
                'complainant_type': 'healthcare_provider',
                'product_name': 'QuickTest Kit V2',
                'product_code': 'QTK-V2-100',
                'product_lot_number': 'LOT2024-023',
                'category': 'labeling',
                'severity': 'minor',
                'priority': 'medium',
                'event_description': 'Instructions missing critical warning',
                'event_location': 'Small Clinic',
                'event_country': 'United States',
                'event_type': 'other',
                'is_reportable_to_fda': False,
            },
            {
                'complaint_id': 'CMP-2025-004',
                'title': 'Packaging Damage Upon Receipt',
                'description': 'Kit arrived with broken reagent vials',
                'complainant_name': 'Receiving Supervisor',
                'complainant_email': 'receiver@hospital.com',
                'complainant_type': 'healthcare_provider',
                'product_name': 'ComprehensivePlex',
                'product_code': 'CPL-PRO-500',
                'product_lot_number': 'LOT2024-089',
                'category': 'packaging',
                'severity': 'major',
                'priority': 'high',
                'event_description': '3 vials broken out of 10',
                'event_location': 'Hospital Warehouse',
                'event_country': 'United States',
                'event_type': 'malfunction',
                'is_reportable_to_fda': False,
            },
            {
                'complaint_id': 'CMP-2025-005',
                'title': 'False Positive Results Reported',
                'description': 'Test giving positive results for negative controls',
                'complainant_name': 'Clinical Lab Director',
                'complainant_email': 'director@medlabs.com',
                'complainant_type': 'healthcare_provider',
                'product_name': 'PathDetect Pro',
                'product_code': 'PDP-100-001',
                'product_lot_number': 'LOT2024-055',
                'category': 'product_performance',
                'severity': 'critical',
                'priority': 'high',
                'event_description': '10% false positive rate in validation run',
                'event_location': 'Reference Lab',
                'event_country': 'United States',
                'event_type': 'malfunction',
                'is_reportable_to_fda': True,
            },
            {
                'complaint_id': 'CMP-2025-006',
                'title': 'Batch Not Meeting Specifications',
                'description': 'Control material out of specification',
                'complainant_name': 'QC Manager',
                'complainant_email': 'qc@hospital.com',
                'complainant_type': 'healthcare_provider',
                'product_name': 'ControlMaterial V3',
                'product_code': 'CM-V3-CTRL',
                'product_lot_number': 'LOT2024-112',
                'category': 'product_quality',
                'severity': 'major',
                'priority': 'medium',
                'event_description': 'Control values outside acceptable range',
                'event_location': 'Central Lab',
                'event_country': 'United States',
                'event_type': 'other',
                'is_reportable_to_fda': False,
            },
        ]

        for data in complaint_data:
            try:
                complaint, created = Complaint.objects.get_or_create(
                    complaint_id=data['complaint_id'],
                    defaults={
                        'title': data['title'],
                        'description': data['description'],
                        'complainant_name': data['complainant_name'],
                        'complainant_email': data['complainant_email'],
                        'complainant_type': data['complainant_type'],
                        'product_name': data['product_name'],
                        'product_code': data['product_code'],
                        'product_lot_number': data['product_lot_number'],
                        'category': data['category'],
                        'severity': data['severity'],
                        'priority': data['priority'],
                        'event_description': data['event_description'],
                        'event_location': data['event_location'],
                        'event_country': data['event_country'],
                        'event_type': data['event_type'],
                        'is_reportable_to_fda': data['is_reportable_to_fda'],
                        'status': 'new',
                        'department': department,
                        'assigned_to': user,
                        'created_by': user,
                        'updated_by': user,
                    }
                )
                if created:
                    self.stdout.write(f"  Created: {complaint.complaint_id}")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  Skipped {data['complaint_id']}: {str(e)}"))

    def seed_deviations(self, user, department):
        """Seed Deviation records"""
        self.stdout.write('Seeding Deviation data...')

        deviation_data = [
            {
                'deviation_id': 'DEV-2025-001',
                'title': 'Temperature Excursion in Incubator',
                'description': 'Incubator temperature exceeded specification',
                'deviation_type': 'unplanned',
                'category': 'equipment',
                'severity': 'critical',
                'source': 'production',
                'process_affected': 'Culture Media Preparation',
                'product_affected': 'All media lots in Incubator 5',
                'impact_assessment': 'High risk to product viability',
                'patient_safety_impact': True,
            },
            {
                'deviation_id': 'DEV-2025-002',
                'title': 'Validation Study Incomplete',
                'description': 'Missing required replicates in validation',
                'deviation_type': 'unplanned',
                'category': 'process',
                'severity': 'major',
                'source': 'self_inspection',
                'process_affected': 'Method Validation',
                'product_affected': 'DiagnoSmart IVD-500',
                'impact_assessment': 'Validation may not meet regulatory requirements',
                'patient_safety_impact': False,
            },
            {
                'deviation_id': 'DEV-2025-003',
                'title': 'Operator Error in Labeling',
                'description': 'Wrong label applied to product batch',
                'deviation_type': 'unplanned',
                'category': 'product',
                'severity': 'major',
                'source': 'production',
                'process_affected': 'Final Labeling & Packaging',
                'product_affected': '500 units of PathDetect Pro',
                'impact_assessment': 'Requires relabeling, schedule impact',
                'patient_safety_impact': False,
            },
            {
                'deviation_id': 'DEV-2025-004',
                'title': 'Component Supply Contamination',
                'description': 'Incoming plastic vials contaminated with particulates',
                'deviation_type': 'unplanned',
                'category': 'material',
                'severity': 'critical',
                'source': 'incoming_inspection',
                'process_affected': 'Material Receiving & QC',
                'product_affected': 'All products in production queue',
                'impact_assessment': 'Batch hold, supplier action required',
                'patient_safety_impact': True,
            },
            {
                'deviation_id': 'DEV-2025-005',
                'title': 'Scheduled Maintenance Completion Delayed',
                'description': 'Equipment maintenance extended beyond planned window',
                'deviation_type': 'planned',
                'category': 'equipment',
                'severity': 'minor',
                'source': 'production',
                'process_affected': 'Manufacturing Schedule',
                'product_affected': 'Production delay 2 days',
                'impact_assessment': 'Minor schedule impact',
                'patient_safety_impact': False,
            },
            {
                'deviation_id': 'DEV-2025-006',
                'title': 'Documentation Review Gap',
                'description': 'SOP not reviewed on scheduled date',
                'deviation_type': 'unplanned',
                'category': 'documentation',
                'severity': 'minor',
                'source': 'audit_finding',
                'process_affected': 'Document Control',
                'product_affected': 'Manufacturing SOPs',
                'impact_assessment': 'Compliance risk if not resolved quickly',
                'patient_safety_impact': False,
            },
        ]

        for data in deviation_data:
            try:
                deviation, created = Deviation.objects.get_or_create(
                    deviation_id=data['deviation_id'],
                    defaults={
                        'title': data['title'],
                        'description': data['description'],
                        'deviation_type': data['deviation_type'],
                        'category': data['category'],
                        'severity': data['severity'],
                        'source': data['source'],
                        'process_affected': data['process_affected'],
                        'product_affected': data['product_affected'],
                        'impact_assessment': data['impact_assessment'],
                        'patient_safety_impact': data['patient_safety_impact'],
                        'current_stage': 'opened',
                        'department': department,
                        'reported_by': user,
                        'assigned_to': user,
                        'created_by': user,
                        'updated_by': user,
                    }
                )
                if created:
                    self.stdout.write(f"  Created: {deviation.deviation_id}")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  Skipped {data['deviation_id']}: {str(e)}"))

    def seed_documents(self, user, department):
        """Seed Document records"""
        self.stdout.write('Seeding Document data...')

        # Get or create document types
        sop_type, _ = DocumentInfocardType.objects.get_or_create(
            prefix='SOP',
            defaults={'name': 'Standard Operating Procedure', 'description': 'Standard operating procedures'}
        )
        wi_type, _ = DocumentInfocardType.objects.get_or_create(
            prefix='WI',
            defaults={'name': 'Work Instruction', 'description': 'Work instructions'}
        )
        form_type, _ = DocumentInfocardType.objects.get_or_create(
            prefix='FRM',
            defaults={'name': 'Form', 'description': 'Forms and templates'}
        )
        policy_type, _ = DocumentInfocardType.objects.get_or_create(
            prefix='POL',
            defaults={'name': 'Policy', 'description': 'Company policies'}
        )

        document_data = [
            {
                'title': 'SOP for Media Preparation',
                'infocard_type': sop_type,
                'vault_state': 'released',
                'business_unit': 'Manufacturing',
                'description': 'Procedure for preparing culture media',
            },
            {
                'title': 'Work Instruction for Filling Line A',
                'infocard_type': wi_type,
                'vault_state': 'released',
                'business_unit': 'Manufacturing',
                'description': 'Step-by-step instructions for operating filling line A',
            },
            {
                'title': 'Product Complaint Investigation Form',
                'infocard_type': form_type,
                'vault_state': 'released',
                'business_unit': 'Quality Assurance',
                'description': 'Form for documenting complaint investigations',
            },
            {
                'title': 'Quality Policy - Document Control',
                'infocard_type': policy_type,
                'vault_state': 'released',
                'business_unit': 'Quality Assurance',
                'description': 'Policy defining document control procedures',
            },
            {
                'title': 'SOP for Deviation Reporting',
                'infocard_type': sop_type,
                'vault_state': 'released',
                'business_unit': 'Quality Assurance',
                'description': 'Process for reporting and investigating deviations',
            },
            {
                'title': 'Work Instruction for Equipment Calibration',
                'infocard_type': wi_type,
                'vault_state': 'draft',
                'business_unit': 'Quality Assurance',
                'description': 'Instructions for calibrating lab equipment',
            },
            {
                'title': 'Change Control Procedure',
                'infocard_type': sop_type,
                'vault_state': 'released',
                'business_unit': 'Operations',
                'description': 'SOP for managing change controls',
            },
            {
                'title': 'Training Documentation Form',
                'infocard_type': form_type,
                'vault_state': 'released',
                'business_unit': 'Human Resources',
                'description': 'Form for tracking training completion',
            },
        ]

        for i, data in enumerate(document_data, start=1):
            try:
                document, created = Document.objects.get_or_create(
                    title=data['title'],
                    defaults={
                        'document_id': f"{data['infocard_type'].prefix}-{i:03d}",
                        'infocard_type': data['infocard_type'],
                        'vault_state': data['vault_state'],
                        'business_unit': data['business_unit'],
                        'department': department,
                        'owner': user,
                        'major_version': 1,
                        'minor_version': 0,
                        'requires_training': False,
                        'confidentiality_level': 'internal',
                        'distribution_restriction': 'none',
                        'created_by': user,
                        'updated_by': user,
                    }
                )
                if created:
                    self.stdout.write(f"  Created: {document.document_id}")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  Skipped {data['title']}: {str(e)}"))

    def seed_training(self, user, department):
        """Seed Training records"""
        self.stdout.write('Seeding Training data...')

        # Create job function
        job_function, _ = JobFunction.objects.get_or_create(
            code='QA001',
            defaults={
                'name': 'Quality Assurance Analyst',
                'description': 'QA analyst role',
                'department': department,
            }
        )

        training_data = [
            {
                'course_id': 'TRN-GMP-001',
                'title': 'Good Manufacturing Practice (GMP) Fundamentals',
                'description': 'Introduction to GMP principles and requirements',
                'course_type': 'classroom',
                'duration_hours': 8.0,
                'status': 'active',
            },
            {
                'course_id': 'TRN-QMS-001',
                'title': 'Quality Management System Overview',
                'description': 'Overview of the company QMS and policies',
                'course_type': 'elearning',
                'duration_hours': 4.0,
                'status': 'active',
            },
            {
                'course_id': 'TRN-CAPA-001',
                'title': 'CAPA Process and Implementation',
                'description': 'Comprehensive CAPA management training',
                'course_type': 'blended',
                'duration_hours': 6.0,
                'status': 'active',
            },
            {
                'course_id': 'TRN-DEV-001',
                'title': 'Deviation Management Training',
                'description': 'How to report and investigate deviations',
                'course_type': 'classroom',
                'duration_hours': 4.0,
                'status': 'active',
            },
            {
                'course_id': 'TRN-DOC-001',
                'title': 'Document Control Procedures',
                'description': 'Managing controlled documents',
                'course_type': 'elearning',
                'duration_hours': 2.0,
                'status': 'active',
            },
            {
                'course_id': 'TRN-AUD-001',
                'title': 'Internal Audit Techniques',
                'description': 'Advanced internal audit skills',
                'course_type': 'classroom',
                'duration_hours': 16.0,
                'status': 'active',
            },
        ]

        for data in training_data:
            try:
                course, created = TrainingCourse.objects.get_or_create(
                    course_id=data['course_id'],
                    defaults={
                        'title': data['title'],
                        'description': data['description'],
                        'course_type': data['course_type'],
                        'duration_hours': data['duration_hours'],
                        'status': data['status'],
                        'department': department,
                        'has_assessment': False,
                        'passing_score_percent': 80,
                        'created_by': user,
                        'updated_by': user,
                    }
                )
                if created:
                    self.stdout.write(f"  Created: {course.course_id}")

                    # Create training assignment
                    due_date = timezone.now() + timedelta(days=30)
                    TrainingAssignment.objects.get_or_create(
                        user=user,
                        course=course,
                        defaults={
                            'due_date': due_date,
                            'status': 'not_started',
                            'assigned_by': user,
                            'created_by': user,
                            'updated_by': user,
                        }
                    )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  Skipped {data['course_id']}: {str(e)}"))

    def seed_suppliers(self, user, department):
        """Seed Supplier records"""
        self.stdout.write('Seeding Supplier data...')

        supplier_data = [
            {
                'supplier_id': 'SUP-RAW-001',
                'name': 'BioChem Materials Inc',
                'supplier_type': 'raw_material',
                'contact_name': 'Tom Wilson',
                'contact_email': 'tom@biochem.com',
                'contact_phone': '+1-555-0101',
                'country': 'United States',
                'qualification_status': 'qualified',
                'risk_level': 'medium',
                'gmp_compliant': True,
            },
            {
                'supplier_id': 'SUP-REAG-002',
                'name': 'ReagentSource Global',
                'supplier_type': 'raw_material',
                'contact_name': 'Maria Garcia',
                'contact_email': 'maria@reagentsource.com',
                'contact_phone': '+1-555-0102',
                'country': 'Germany',
                'qualification_status': 'qualified',
                'risk_level': 'high',
                'gmp_compliant': True,
            },
            {
                'supplier_id': 'SUP-PKG-003',
                'name': 'PlastiTech Packaging',
                'supplier_type': 'component',
                'contact_name': 'John Chen',
                'contact_email': 'john@plastitech.com',
                'contact_phone': '+1-555-0103',
                'country': 'United States',
                'qualification_status': 'qualified',
                'risk_level': 'medium',
                'gmp_compliant': False,
            },
            {
                'supplier_id': 'SUP-CAL-004',
                'name': 'PrecisionCal Services',
                'supplier_type': 'calibration',
                'contact_name': 'Sarah Brown',
                'contact_email': 'sarah@precisioncal.com',
                'contact_phone': '+1-555-0104',
                'country': 'United States',
                'qualification_status': 'qualified',
                'risk_level': 'low',
                'gmp_compliant': False,
            },
            {
                'supplier_id': 'SUP-DIST-005',
                'name': 'Global Healthcare Distributors',
                'supplier_type': 'distributor',
                'contact_name': 'Robert Davis',
                'contact_email': 'robert@globaldist.com',
                'contact_phone': '+1-555-0105',
                'country': 'United States',
                'qualification_status': 'pending_evaluation',
                'risk_level': 'medium',
                'gmp_compliant': False,
            },
        ]

        for data in supplier_data:
            try:
                supplier, created = Supplier.objects.get_or_create(
                    supplier_id=data['supplier_id'],
                    defaults={
                        'name': data['name'],
                        'supplier_type': data['supplier_type'],
                        'contact_name': data['contact_name'],
                        'contact_email': data['contact_email'],
                        'contact_phone': data['contact_phone'],
                        'country': data['country'],
                        'qualification_status': data['qualification_status'],
                        'risk_level': data['risk_level'],
                        'gmp_compliant': data['gmp_compliant'],
                        'department': department,
                        'quality_contact': user,
                        'created_by': user,
                        'updated_by': user,
                    }
                )
                if created:
                    self.stdout.write(f"  Created: {supplier.supplier_id}")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  Skipped {data['supplier_id']}: {str(e)}"))

    def seed_change_controls(self, user, department):
        """Seed Change Control records"""
        self.stdout.write('Seeding Change Control data...')

        change_data = [
            {
                'change_control_id': 'CC-2025-001',
                'title': 'Update Manufacturing SOP for Filling Line A',
                'description': 'Implement new aseptic filling parameters',
                'change_type': 'process',
                'change_category': 'major',
                'risk_level': 'high',
                'current_stage': 'screening',
            },
            {
                'change_control_id': 'CC-2025-002',
                'title': 'Upgrade LIMS Software Version',
                'description': 'Update to latest LIMS version for enhanced reporting',
                'change_type': 'system',
                'change_category': 'minor',
                'risk_level': 'medium',
                'current_stage': 'impact_assessment',
            },
            {
                'change_control_id': 'CC-2025-003',
                'title': 'Supplier Change: Reagent Manufacturer',
                'description': 'Switch reagent supplier due to quality improvement',
                'change_type': 'supplier',
                'change_category': 'major',
                'risk_level': 'high',
                'current_stage': 'approval',
            },
            {
                'change_control_id': 'CC-2025-004',
                'title': 'Equipment Maintenance Schedule Update',
                'description': 'Adjust calibration intervals based on usage data',
                'change_type': 'equipment',
                'change_category': 'minor',
                'risk_level': 'low',
                'current_stage': 'implementation',
            },
        ]

        for data in change_data:
            try:
                cc, created = ChangeControl.objects.get_or_create(
                    change_control_id=data['change_control_id'],
                    defaults={
                        'title': data['title'],
                        'description': data['description'],
                        'change_type': data['change_type'],
                        'change_category': data['change_category'],
                        'risk_level': data['risk_level'],
                        'current_stage': data['current_stage'],
                        'department': department,
                        'proposed_by': user,
                        'assigned_to': user,
                        'created_by': user,
                        'updated_by': user,
                    }
                )
                if created:
                    self.stdout.write(f"  Created: {cc.change_control_id}")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  Skipped {data['change_control_id']}: {str(e)}"))

    def seed_audits(self, user, department):
        """Seed Audit records"""
        self.stdout.write('Seeding Audit data...')

        audit_data = [
            {
                'audit_id': 'AUD-2025-001',
                'audit_type': 'internal',
                'scope': 'Manufacturing processes and SOPs',
                'status': 'completed',
                'planned_start': timezone.now().date() - timedelta(days=30),
                'planned_end': timezone.now().date() - timedelta(days=28),
                'actual_start': timezone.now().date() - timedelta(days=30),
                'actual_end': timezone.now().date() - timedelta(days=28),
            },
            {
                'audit_id': 'AUD-2025-002',
                'audit_type': 'supplier',
                'scope': 'Raw material supplier qualification',
                'status': 'completed',
                'planned_start': timezone.now().date() - timedelta(days=20),
                'planned_end': timezone.now().date() - timedelta(days=18),
                'supplier_name': 'BioChem Materials Inc',
            },
            {
                'audit_id': 'AUD-2025-003',
                'audit_type': 'internal',
                'scope': 'Quality systems and documentation',
                'status': 'in_progress',
                'planned_start': timezone.now().date() - timedelta(days=5),
                'planned_end': timezone.now().date() + timedelta(days=2),
            },
            {
                'audit_id': 'AUD-2025-004',
                'audit_type': 'internal',
                'scope': 'Complaint handling and CAPA management',
                'status': 'planned',
                'planned_start': timezone.now().date() + timedelta(days=15),
                'planned_end': timezone.now().date() + timedelta(days=17),
            },
        ]

        for data in audit_data:
            try:
                audit, created = AuditPlan.objects.get_or_create(
                    audit_id=data['audit_id'],
                    defaults={
                        'audit_type': data['audit_type'],
                        'scope': data['scope'],
                        'status': data['status'],
                        'planned_start_date': data['planned_start'],
                        'planned_end_date': data['planned_end'],
                        'actual_start_date': data.get('actual_start'),
                        'actual_end_date': data.get('actual_end'),
                        'supplier': data.get('supplier_name', ''),
                        'lead_auditor': user,
                        'created_by': user,
                        'updated_by': user,
                    }
                )
                if created:
                    self.stdout.write(f"  Created: {audit.audit_id}")

                    # Create sample audit findings for completed audits
                    if audit.status == 'completed' and not audit.findings.exists():
                        findings = [
                            {
                                'finding_id': f'AF-{data["audit_id"]}-001',
                                'category': 'minor_nc',
                                'description': 'Minor documentation gap identified',
                                'evidence': 'SOP-001 revision date missing',
                            },
                            {
                                'finding_id': f'AF-{data["audit_id"]}-002',
                                'category': 'observation',
                                'description': 'Opportunity for process improvement',
                                'evidence': 'Current procedure could be streamlined',
                            },
                        ]

                        for finding in findings:
                            try:
                                AuditFinding.objects.get_or_create(
                                    finding_id=finding['finding_id'],
                                    defaults={
                                        'audit': audit,
                                        'category': finding['category'],
                                        'description': finding['description'],
                                        'evidence': finding['evidence'],
                                        'status': 'open',
                                        'created_by': user,
                                        'updated_by': user,
                                    }
                                )
                            except Exception as e:
                                self.stdout.write(self.style.WARNING(f"    Skipped {finding['finding_id']}: {str(e)}"))

            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  Skipped {data['audit_id']}: {str(e)}"))
