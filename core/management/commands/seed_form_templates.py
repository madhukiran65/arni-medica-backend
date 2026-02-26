from django.core.management.base import BaseCommand
from forms.models import FormTemplate, FormSection, FormQuestion


class Command(BaseCommand):
    help = 'Seed form templates relevant to IVD/pharmaceutical eQMS'

    def handle(self, *args, **options):
        # Template 1: Internal Audit Checklist
        audit_template, created = FormTemplate.objects.get_or_create(
            name='Internal Audit Checklist',
            defaults={
                'description': 'Comprehensive internal audit checklist for quality system assessment',
                'template_type': 'audit_checklist',
                'version': '1.0',
                'is_published': True,
                'is_active': True,
                'category': 'Quality Management',
            }
        )
        if created:
            self._create_audit_sections(audit_template)
            self.stdout.write(self.style.SUCCESS(f'Created: {audit_template.name}'))
        else:
            self.stdout.write(f'Already exists: {audit_template.name}')

        # Template 2: Deviation Investigation Form
        deviation_template, created = FormTemplate.objects.get_or_create(
            name='Deviation Investigation Form',
            defaults={
                'description': 'Form for investigating and documenting deviations from standard procedures',
                'template_type': 'investigation_form',
                'version': '1.0',
                'is_published': True,
                'is_active': True,
                'category': 'Quality Management',
            }
        )
        if created:
            self._create_deviation_sections(deviation_template)
            self.stdout.write(self.style.SUCCESS(f'Created: {deviation_template.name}'))
        else:
            self.stdout.write(f'Already exists: {deviation_template.name}')

        # Template 3: Incoming Material Inspection
        inspection_template, created = FormTemplate.objects.get_or_create(
            name='Incoming Material Inspection',
            defaults={
                'description': 'Inspection form for incoming materials and supplier shipments',
                'template_type': 'inspection_form',
                'version': '1.0',
                'is_published': True,
                'is_active': True,
                'category': 'Supplier Quality',
            }
        )
        if created:
            self._create_inspection_sections(inspection_template)
            self.stdout.write(self.style.SUCCESS(f'Created: {inspection_template.name}'))
        else:
            self.stdout.write(f'Already exists: {inspection_template.name}')

        # Template 4: Supplier Qualification Questionnaire
        supplier_template, created = FormTemplate.objects.get_or_create(
            name='Supplier Qualification Questionnaire',
            defaults={
                'description': 'Questionnaire for supplier qualification and assessment',
                'template_type': 'review_form',
                'version': '1.0',
                'is_published': True,
                'is_active': True,
                'category': 'Supplier Quality',
            }
        )
        if created:
            self._create_supplier_sections(supplier_template)
            self.stdout.write(self.style.SUCCESS(f'Created: {supplier_template.name}'))
        else:
            self.stdout.write(f'Already exists: {supplier_template.name}')

        # Template 5: Equipment Calibration Log
        calibration_template, created = FormTemplate.objects.get_or_create(
            name='Equipment Calibration Log',
            defaults={
                'description': 'Log for tracking equipment calibration activities and results',
                'template_type': 'custom',
                'version': '1.0',
                'is_published': False,
                'is_active': True,
                'category': 'Equipment Management',
            }
        )
        if created:
            self._create_calibration_sections(calibration_template)
            self.stdout.write(self.style.SUCCESS(f'Created: {calibration_template.name}'))
        else:
            self.stdout.write(f'Already exists: {calibration_template.name}')

        self.stdout.write(self.style.SUCCESS('Successfully seeded form templates'))

    def _create_audit_sections(self, template):
        """Create sections for Internal Audit Checklist"""
        sections_data = [
            {
                'title': 'Audit Information',
                'description': 'Basic information about the audit',
                'sequence': 1,
                'questions': [
                    ('Audit Date', 'date', True, 1),
                    ('Audited Department', 'text', True, 2),
                    ('Audit Scope', 'textarea', True, 3),
                    ('Lead Auditor', 'text', True, 4),
                ]
            },
            {
                'title': 'Documentation Review',
                'description': 'Review of documentation and records',
                'sequence': 2,
                'questions': [
                    ('Standard Operating Procedures reviewed', 'checkbox', True, 1),
                    ('Records and documentation complete', 'checkbox', True, 2),
                    ('Issues found', 'textarea', False, 3),
                ]
            },
            {
                'title': 'Process Assessment',
                'description': 'Assessment of operational processes',
                'sequence': 3,
                'questions': [
                    ('Process follows documented procedures', 'radio', True, 1),
                    ('Process effectiveness rating', 'rating', True, 2),
                    ('Process observations', 'textarea', False, 3),
                ]
            },
            {
                'title': 'Equipment/Facility',
                'description': 'Assessment of equipment and facilities',
                'sequence': 4,
                'questions': [
                    ('Equipment maintained and calibrated', 'checkbox', True, 1),
                    ('Facility cleanliness acceptable', 'checkbox', True, 2),
                    ('Equipment/Facility findings', 'textarea', False, 3),
                ]
            },
            {
                'title': 'Findings Summary',
                'description': 'Summary of audit findings and recommendations',
                'sequence': 5,
                'questions': [
                    ('Number of findings', 'number', True, 1),
                    ('Major findings', 'textarea', False, 2),
                    ('Minor observations', 'textarea', False, 3),
                    ('Recommendations for improvement', 'textarea', False, 4),
                    ('Auditor Sign-off', 'signature', True, 5),
                ]
            }
        ]

        for section_data in sections_data:
            questions = section_data.pop('questions')
            section, _ = FormSection.objects.get_or_create(
                template=template,
                sequence=section_data['sequence'],
                defaults={
                    'title': section_data['title'],
                    'description': section_data['description'],
                    'is_repeatable': False,
                }
            )

            for q_text, q_type, is_required, seq in questions:
                FormQuestion.objects.get_or_create(
                    section=section,
                    sequence=seq,
                    defaults={
                        'question_text': q_text,
                        'question_type': q_type,
                        'is_required': is_required,
                        'help_text': '',
                    }
                )

    def _create_deviation_sections(self, template):
        """Create sections for Deviation Investigation Form"""
        sections_data = [
            {
                'title': 'Deviation Details',
                'description': 'Description of the deviation',
                'sequence': 1,
                'questions': [
                    ('Deviation ID', 'text', True, 1),
                    ('Date Detected', 'date', True, 2),
                    ('Department/Area', 'text', True, 3),
                    ('Description of Deviation', 'textarea', True, 4),
                    ('Product/Process Affected', 'text', True, 5),
                ]
            },
            {
                'title': 'Initial Assessment',
                'description': 'Initial assessment of the deviation',
                'sequence': 2,
                'questions': [
                    ('Severity Level', 'dropdown', True, 1),
                    ('Immediate Action Taken', 'textarea', True, 2),
                    ('Affected Product/Batch Quantity', 'number', True, 3),
                ]
            },
            {
                'title': 'Root Cause Investigation',
                'description': 'Investigation to determine root cause',
                'sequence': 3,
                'questions': [
                    ('Investigation Method', 'dropdown', True, 1),
                    ('Root Cause Identified', 'textarea', True, 2),
                    ('Contributing Factors', 'textarea', False, 3),
                ]
            },
            {
                'title': 'Impact Assessment',
                'description': 'Assessment of deviation impact',
                'sequence': 4,
                'questions': [
                    ('Quality Impact', 'textarea', True, 1),
                    ('Customer Notification Required', 'radio', True, 2),
                    ('Regulatory Impact', 'textarea', False, 3),
                ]
            },
            {
                'title': 'Corrective Actions',
                'description': 'Define and track corrective actions',
                'sequence': 5,
                'questions': [
                    ('Corrective Action(s)', 'textarea', True, 1),
                    ('Preventive Action(s)', 'textarea', False, 2),
                    ('Target Completion Date', 'date', True, 3),
                    ('Investigation Completed By', 'text', True, 4),
                    ('Manager Sign-off', 'signature', True, 5),
                ]
            }
        ]

        for section_data in sections_data:
            questions = section_data.pop('questions')
            section, _ = FormSection.objects.get_or_create(
                template=template,
                sequence=section_data['sequence'],
                defaults={
                    'title': section_data['title'],
                    'description': section_data['description'],
                    'is_repeatable': False,
                }
            )

            for q_text, q_type, is_required, seq in questions:
                FormQuestion.objects.get_or_create(
                    section=section,
                    sequence=seq,
                    defaults={
                        'question_text': q_text,
                        'question_type': q_type,
                        'is_required': is_required,
                        'help_text': '',
                    }
                )

    def _create_inspection_sections(self, template):
        """Create sections for Incoming Material Inspection"""
        sections_data = [
            {
                'title': 'Material Information',
                'description': 'Details of the incoming material',
                'sequence': 1,
                'questions': [
                    ('Supplier Name', 'text', True, 1),
                    ('Material Description', 'text', True, 2),
                    ('Lot/Batch Number', 'text', True, 3),
                    ('Purchase Order Number', 'text', True, 4),
                    ('Quantity Received', 'number', True, 5),
                    ('Date Received', 'date', True, 6),
                ]
            },
            {
                'title': 'Visual Inspection',
                'description': 'Visual inspection of material condition',
                'sequence': 2,
                'questions': [
                    ('Packaging Condition', 'radio', True, 1),
                    ('Product Appearance', 'radio', True, 2),
                    ('Visible Defects Found', 'checkbox', False, 3),
                    ('Defect Description', 'textarea', False, 4),
                ]
            },
            {
                'title': 'Documentation Check',
                'description': 'Verification of supplier documentation',
                'sequence': 3,
                'questions': [
                    ('Certificate of Analysis Present', 'checkbox', True, 1),
                    ('Certificate of Conformance Present', 'checkbox', True, 2),
                    ('Test Reports Present', 'checkbox', False, 3),
                    ('Documentation Issues', 'textarea', False, 4),
                ]
            },
            {
                'title': 'Sampling & Testing',
                'description': 'Sampling and test results',
                'sequence': 4,
                'questions': [
                    ('Samples Taken', 'checkbox', True, 1),
                    ('Sample Quantity', 'number', False, 2),
                    ('Testing Required', 'checkbox', False, 3),
                    ('Test Results', 'textarea', False, 4),
                    ('Test Status', 'dropdown', False, 5),
                ]
            },
            {
                'title': 'Accept/Reject Decision',
                'description': 'Final acceptance or rejection decision',
                'sequence': 5,
                'questions': [
                    ('Inspection Decision', 'radio', True, 1),
                    ('Quantity Accepted', 'number', True, 2),
                    ('Quantity Rejected', 'number', False, 3),
                    ('Rejection Reason', 'textarea', False, 4),
                    ('Inspector Name', 'text', True, 5),
                    ('Inspector Signature', 'signature', True, 6),
                ]
            }
        ]

        for section_data in sections_data:
            questions = section_data.pop('questions')
            section, _ = FormSection.objects.get_or_create(
                template=template,
                sequence=section_data['sequence'],
                defaults={
                    'title': section_data['title'],
                    'description': section_data['description'],
                    'is_repeatable': False,
                }
            )

            for q_text, q_type, is_required, seq in questions:
                FormQuestion.objects.get_or_create(
                    section=section,
                    sequence=seq,
                    defaults={
                        'question_text': q_text,
                        'question_type': q_type,
                        'is_required': is_required,
                        'help_text': '',
                    }
                )

    def _create_supplier_sections(self, template):
        """Create sections for Supplier Qualification Questionnaire"""
        sections_data = [
            {
                'title': 'Company Information',
                'description': 'Basic company and contact information',
                'sequence': 1,
                'questions': [
                    ('Company Name', 'text', True, 1),
                    ('Business Address', 'text', True, 2),
                    ('Contact Person', 'text', True, 3),
                    ('Contact Email', 'email', True, 4),
                    ('Contact Phone', 'phone', True, 5),
                    ('Years in Business', 'number', True, 6),
                ]
            },
            {
                'title': 'Quality System',
                'description': 'Quality management system information',
                'sequence': 2,
                'questions': [
                    ('ISO 13485 Certified', 'checkbox', True, 1),
                    ('Certification Number', 'text', False, 2),
                    ('Certifying Body', 'text', False, 3),
                    ('Quality Manager Name', 'text', True, 4),
                    ('Quality System Description', 'textarea', True, 5),
                ]
            },
            {
                'title': 'Regulatory Compliance',
                'description': 'Regulatory and compliance information',
                'sequence': 3,
                'questions': [
                    ('FDA Registration Number', 'text', False, 1),
                    ('GMP Compliant', 'radio', True, 2),
                    ('Regulatory Approvals', 'textarea', False, 3),
                    ('Any Regulatory Actions', 'radio', True, 4),
                    ('Action Details', 'textarea', False, 5),
                ]
            },
            {
                'title': 'Manufacturing Capabilities',
                'description': 'Manufacturing and production capabilities',
                'sequence': 4,
                'questions': [
                    ('Products/Services Offered', 'textarea', True, 1),
                    ('Production Capacity', 'number', True, 2),
                    ('Lead Time (days)', 'number', True, 3),
                    ('Minimum Order Quantity', 'number', True, 4),
                    ('Special Equipment/Capabilities', 'textarea', False, 5),
                ]
            },
            {
                'title': 'References',
                'description': 'Customer references and supporting information',
                'sequence': 5,
                'questions': [
                    ('Reference Customer 1', 'text', True, 1),
                    ('Reference Contact 1', 'text', True, 2),
                    ('Reference Customer 2', 'text', False, 3),
                    ('Reference Contact 2', 'text', False, 4),
                    ('Additional Documents', 'file_upload', False, 5),
                    ('Approved By', 'text', True, 6),
                ]
            }
        ]

        for section_data in sections_data:
            questions = section_data.pop('questions')
            section, _ = FormSection.objects.get_or_create(
                template=template,
                sequence=section_data['sequence'],
                defaults={
                    'title': section_data['title'],
                    'description': section_data['description'],
                    'is_repeatable': False,
                }
            )

            for q_text, q_type, is_required, seq in questions:
                FormQuestion.objects.get_or_create(
                    section=section,
                    sequence=seq,
                    defaults={
                        'question_text': q_text,
                        'question_type': q_type,
                        'is_required': is_required,
                        'help_text': '',
                    }
                )

    def _create_calibration_sections(self, template):
        """Create sections for Equipment Calibration Log"""
        sections_data = [
            {
                'title': 'Equipment Details',
                'description': 'Information about the equipment being calibrated',
                'sequence': 1,
                'questions': [
                    ('Equipment Name', 'text', True, 1),
                    ('Equipment ID/Serial Number', 'text', True, 2),
                    ('Equipment Type', 'dropdown', True, 3),
                    ('Manufacturer', 'text', True, 4),
                    ('Model Number', 'text', True, 5),
                    ('Calibration Date', 'date', True, 6),
                ]
            },
            {
                'title': 'Calibration Standards',
                'description': 'Standards and reference materials used',
                'sequence': 2,
                'questions': [
                    ('Standard Used', 'text', True, 1),
                    ('Standard Certification Number', 'text', True, 2),
                    ('Standard Accuracy', 'text', True, 3),
                    ('Temperature During Calibration', 'number', False, 4),
                    ('Environmental Conditions', 'textarea', False, 5),
                ]
            },
            {
                'title': 'Measurements',
                'description': 'Calibration measurements and results',
                'sequence': 3,
                'questions': [
                    ('Measurement Point 1 Value', 'number', True, 1),
                    ('Measurement Point 1 Expected', 'number', True, 2),
                    ('Measurement Point 2 Value', 'number', False, 3),
                    ('Measurement Point 2 Expected', 'number', False, 4),
                    ('Measurement Point 3 Value', 'number', False, 5),
                    ('Measurement Point 3 Expected', 'number', False, 6),
                ]
            },
            {
                'title': 'Pass/Fail Criteria',
                'description': 'Assessment of calibration results',
                'sequence': 4,
                'questions': [
                    ('Tolerance Range', 'text', True, 1),
                    ('All Measurements Within Tolerance', 'radio', True, 2),
                    ('Calibration Status', 'dropdown', True, 3),
                    ('Out of Tolerance Details', 'textarea', False, 4),
                    ('Action Taken', 'textarea', False, 5),
                ]
            },
            {
                'title': 'Technician Sign-off',
                'description': 'Calibration completion and approval',
                'sequence': 5,
                'questions': [
                    ('Calibration Completed By', 'text', True, 1),
                    ('Technician Signature', 'signature', True, 2),
                    ('Next Calibration Due Date', 'date', True, 3),
                    ('Notes/Comments', 'textarea', False, 4),
                ]
            }
        ]

        for section_data in sections_data:
            questions = section_data.pop('questions')
            section, _ = FormSection.objects.get_or_create(
                template=template,
                sequence=section_data['sequence'],
                defaults={
                    'title': section_data['title'],
                    'description': section_data['description'],
                    'is_repeatable': False,
                }
            )

            for q_text, q_type, is_required, seq in questions:
                FormQuestion.objects.get_or_create(
                    section=section,
                    sequence=seq,
                    defaults={
                        'question_text': q_text,
                        'question_type': q_type,
                        'is_required': is_required,
                        'help_text': '',
                    }
                )
