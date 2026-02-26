from django.test import TestCase
from django.contrib.auth.models import User
from .models import (
    RiskCategory, Hazard, RiskAssessment, RiskMitigation,
    FMEAWorksheet, FMEARecord, RiskReport, RiskMonitoringAlert
)


class RiskCategoryTestCase(TestCase):
    def setUp(self):
        self.category = RiskCategory.objects.create(
            name='Design Hazards',
            description='Hazards related to product design'
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Design Hazards')
        self.assertTrue(self.category.is_active)

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Design Hazards')


class HazardTestCase(TestCase):
    def setUp(self):
        self.category = RiskCategory.objects.create(name='Test Category')
        self.hazard = Hazard.objects.create(
            name='Test Hazard',
            category=self.category,
            source='design',
            harm_description='Test harm',
            status='identified'
        )

    def test_hazard_id_generation(self):
        self.assertEqual(self.hazard.hazard_id, 'HAZ-0001')

    def test_hazard_str(self):
        self.assertIn('HAZ-0001', str(self.hazard))

    def test_multiple_hazard_ids(self):
        hazard2 = Hazard.objects.create(
            name='Test Hazard 2',
            category=self.category,
            source='manufacturing',
            harm_description='Test harm 2',
            status='identified'
        )
        self.assertEqual(hazard2.hazard_id, 'HAZ-0002')


class RiskAssessmentTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.category = RiskCategory.objects.create(name='Test Category')
        self.hazard = Hazard.objects.create(
            name='Test Hazard',
            category=self.category,
            source='design',
            harm_description='Test harm'
        )

    def test_rpn_calculation(self):
        assessment = RiskAssessment.objects.create(
            hazard=self.hazard,
            assessment_type='initial',
            severity=3,
            occurrence=2,
            detection=2,
            acceptability='alara',
            assessed_by=self.user
        )
        self.assertEqual(assessment.rpn, 12)

    def test_risk_level_critical(self):
        assessment = RiskAssessment.objects.create(
            hazard=self.hazard,
            assessment_type='initial',
            severity=5,
            occurrence=5,
            detection=4,
            acceptability='unacceptable',
            assessed_by=self.user
        )
        self.assertEqual(assessment.risk_level, 'critical')

    def test_risk_level_high(self):
        assessment = RiskAssessment.objects.create(
            hazard=self.hazard,
            assessment_type='initial',
            severity=4,
            occurrence=3,
            detection=4,
            acceptability='conditional',
            assessed_by=self.user
        )
        self.assertEqual(assessment.risk_level, 'high')

    def test_risk_level_low(self):
        assessment = RiskAssessment.objects.create(
            hazard=self.hazard,
            assessment_type='initial',
            severity=1,
            occurrence=2,
            detection=2,
            acceptability='acceptable',
            assessed_by=self.user
        )
        self.assertEqual(assessment.risk_level, 'low')


class FMEAWorksheetTestCase(TestCase):
    def setUp(self):
        self.worksheet = FMEAWorksheet.objects.create(
            title='Test FMEA',
            fmea_type='design',
            status='draft'
        )

    def test_fmea_id_generation(self):
        self.assertEqual(self.worksheet.fmea_id, 'FMEA-0001')

    def test_fmea_str(self):
        self.assertIn('FMEA-0001', str(self.worksheet))


class FMEARecordTestCase(TestCase):
    def setUp(self):
        self.worksheet = FMEAWorksheet.objects.create(
            title='Test FMEA',
            fmea_type='design',
            status='draft'
        )
        self.record = FMEARecord.objects.create(
            worksheet=self.worksheet,
            item_function='Test Function',
            failure_mode='Test Failure',
            failure_effect='Test Effect',
            failure_cause='Test Cause',
            severity=5,
            occurrence=4,
            detection=3
        )

    def test_record_rpn_calculation(self):
        self.assertEqual(self.record.rpn, 60)

    def test_record_new_rpn_calculation(self):
        self.record.new_severity = 3
        self.record.new_occurrence = 2
        self.record.new_detection = 2
        self.assertEqual(self.record.new_rpn, 12)

    def test_record_new_rpn_none(self):
        self.assertIsNone(self.record.new_rpn)


class RiskReportTestCase(TestCase):
    def setUp(self):
        self.report = RiskReport.objects.create(
            title='Test Report',
            report_type='initial_risk_analysis',
            overall_risk_acceptability='acceptable',
            status='draft'
        )

    def test_report_id_generation(self):
        self.assertEqual(self.report.report_id, 'RR-0001')

    def test_report_str(self):
        self.assertIn('RR-0001', str(self.report))


class RiskMonitoringAlertTestCase(TestCase):
    def setUp(self):
        self.category = RiskCategory.objects.create(name='Test Category')
        self.hazard = Hazard.objects.create(
            name='Test Hazard',
            category=self.category,
            source='design',
            harm_description='Test harm'
        )
        self.alert = RiskMonitoringAlert.objects.create(
            hazard=self.hazard,
            alert_type='threshold_breach',
            message='Test message'
        )

    def test_alert_creation(self):
        self.assertFalse(self.alert.is_acknowledged)
        self.assertIsNone(self.alert.acknowledged_at)
