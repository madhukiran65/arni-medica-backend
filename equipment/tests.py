from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from equipment.models import (
    Equipment,
    EquipmentQualification,
    CalibrationSchedule,
    CalibrationRecord,
    MaintenanceSchedule,
    MaintenanceRecord,
    EquipmentDocument,
)


class EquipmentModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_equipment_creation(self):
        equipment = Equipment.objects.create(
            name='Test Equipment',
            equipment_type='laboratory',
            category='calibrated_instrument',
            serial_number='SN123456',
            model_number='MODEL-001',
            manufacturer='Test Manufacturer',
            status='active',
            created_by=self.user,
        )
        self.assertTrue(equipment.equipment_id.startswith('EQ-'))
        self.assertEqual(equipment.name, 'Test Equipment')

    def test_equipment_id_auto_generation(self):
        eq1 = Equipment.objects.create(
            name='Equipment 1',
            equipment_type='laboratory',
            category='calibrated_instrument',
            serial_number='SN001',
            model_number='MOD-001',
            manufacturer='Manufacturer A',
            created_by=self.user,
        )
        eq2 = Equipment.objects.create(
            name='Equipment 2',
            equipment_type='testing',
            category='direct_product_contact',
            serial_number='SN002',
            model_number='MOD-002',
            manufacturer='Manufacturer B',
            created_by=self.user,
        )
        self.assertEqual(eq1.equipment_id, 'EQ-0001')
        self.assertEqual(eq2.equipment_id, 'EQ-0002')


class CalibrationScheduleTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.equipment = Equipment.objects.create(
            name='Calibration Test Equipment',
            equipment_type='laboratory',
            category='calibrated_instrument',
            serial_number='CAL-SN001',
            model_number='CAL-MOD-001',
            manufacturer='Calibration Manufacturer',
            requires_calibration=True,
            created_by=self.user,
        )

    def test_calibration_schedule_creation(self):
        schedule = CalibrationSchedule.objects.create(
            equipment=self.equipment,
            interval_days=365,
        )
        self.assertEqual(schedule.interval_days, 365)
        self.assertFalse(schedule.is_overdue())

    def test_overdue_calibration(self):
        schedule = CalibrationSchedule.objects.create(
            equipment=self.equipment,
            interval_days=365,
            next_due=timezone.now().date() - timedelta(days=1),
        )
        self.assertTrue(schedule.is_overdue())


class CalibrationRecordTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.equipment = Equipment.objects.create(
            name='Record Test Equipment',
            equipment_type='laboratory',
            category='calibrated_instrument',
            serial_number='REC-SN001',
            model_number='REC-MOD-001',
            manufacturer='Record Manufacturer',
            created_by=self.user,
        )

    def test_calibration_record_creation(self):
        record = CalibrationRecord.objects.create(
            equipment=self.equipment,
            calibration_date=timezone.now().date(),
            result='pass',
            calibration_type='internal',
            created_by=self.user,
        )
        self.assertTrue(record.calibration_id.startswith('CAL-'))
        self.assertEqual(record.result, 'pass')

    def test_calibration_record_id_auto_generation(self):
        rec1 = CalibrationRecord.objects.create(
            equipment=self.equipment,
            calibration_date=timezone.now().date(),
            result='pass',
            calibration_type='internal',
            created_by=self.user,
        )
        rec2 = CalibrationRecord.objects.create(
            equipment=self.equipment,
            calibration_date=timezone.now().date(),
            result='fail',
            calibration_type='external',
            created_by=self.user,
        )
        self.assertEqual(rec1.calibration_id, 'CAL-0001')
        self.assertEqual(rec2.calibration_id, 'CAL-0002')


class MaintenanceRecordTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.equipment = Equipment.objects.create(
            name='Maintenance Test Equipment',
            equipment_type='manufacturing',
            category='direct_product_contact',
            serial_number='MAINT-SN001',
            model_number='MAINT-MOD-001',
            manufacturer='Maintenance Manufacturer',
            created_by=self.user,
        )

    def test_maintenance_record_creation(self):
        record = MaintenanceRecord.objects.create(
            equipment=self.equipment,
            maintenance_date=timezone.now().date(),
            maintenance_type='preventive',
            status='completed',
            performed_by=self.user,
            created_by=self.user,
        )
        self.assertTrue(record.maintenance_id.startswith('MR-'))
        self.assertEqual(record.status, 'completed')

    def test_maintenance_record_id_auto_generation(self):
        mr1 = MaintenanceRecord.objects.create(
            equipment=self.equipment,
            maintenance_date=timezone.now().date(),
            maintenance_type='preventive',
            status='completed',
            performed_by=self.user,
            created_by=self.user,
        )
        mr2 = MaintenanceRecord.objects.create(
            equipment=self.equipment,
            maintenance_date=timezone.now().date(),
            maintenance_type='corrective',
            status='completed',
            performed_by=self.user,
            created_by=self.user,
        )
        self.assertEqual(mr1.maintenance_id, 'MR-0001')
        self.assertEqual(mr2.maintenance_id, 'MR-0002')
