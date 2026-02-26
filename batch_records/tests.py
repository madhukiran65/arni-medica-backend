from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import (
    MasterBatchRecord,
    BatchRecord,
    BatchStep,
    BatchDeviation,
    BatchMaterial,
    BatchEquipment,
)


class MasterBatchRecordTestCase(TestCase):
    """Test cases for MasterBatchRecord model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.mbr = MasterBatchRecord.objects.create(
            title='Test MBR',
            product_name='Test Product',
            product_code='TP-001',
            version='1.0',
            created_by=self.user
        )

    def test_mbr_creation(self):
        """Test creating a master batch record."""
        self.assertEqual(self.mbr.title, 'Test MBR')
        self.assertEqual(self.mbr.status, 'draft')
        self.assertTrue(self.mbr.mbr_id.startswith('MBR-'))

    def test_mbr_auto_id_generation(self):
        """Test auto ID generation."""
        mbr2 = MasterBatchRecord.objects.create(
            title='Test MBR 2',
            product_name='Test Product 2',
            product_code='TP-002',
            created_by=self.user
        )
        self.assertIsNotNone(mbr2.mbr_id)
        self.assertNotEqual(self.mbr.mbr_id, mbr2.mbr_id)

    def test_approve_mbr(self):
        """Test approving a master batch record."""
        self.mbr.approve(self.user)
        self.assertEqual(self.mbr.status, 'approved')
        self.assertEqual(self.mbr.approved_by, self.user)
        self.assertIsNotNone(self.mbr.approval_date)

    def test_supersede_mbr(self):
        """Test superseding a master batch record."""
        self.mbr.supersede()
        self.assertEqual(self.mbr.status, 'superseded')

    def test_obsolete_mbr(self):
        """Test marking as obsolete."""
        self.mbr.obsolete()
        self.assertEqual(self.mbr.status, 'obsolete')


class BatchRecordTestCase(TestCase):
    """Test cases for BatchRecord model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.mbr = MasterBatchRecord.objects.create(
            title='Test MBR',
            product_name='Test Product',
            product_code='TP-001',
            created_by=self.user
        )
        self.batch = BatchRecord.objects.create(
            batch_number='BATCH-001',
            lot_number='LOT-001',
            mbr=self.mbr,
            quantity_planned=1000,
            created_by=self.user
        )

    def test_batch_creation(self):
        """Test creating a batch record."""
        self.assertEqual(self.batch.batch_number, 'BATCH-001')
        self.assertEqual(self.batch.status, 'pending')
        self.assertTrue(self.batch.batch_id.startswith('BR-'))

    def test_batch_auto_id_generation(self):
        """Test auto ID generation for batch."""
        batch2 = BatchRecord.objects.create(
            batch_number='BATCH-002',
            lot_number='LOT-002',
            mbr=self.mbr,
            quantity_planned=500,
            created_by=self.user
        )
        self.assertIsNotNone(batch2.batch_id)
        self.assertNotEqual(self.batch.batch_id, batch2.batch_id)

    def test_start_production(self):
        """Test starting batch production."""
        self.batch.start_production()
        self.assertEqual(self.batch.status, 'in_progress')
        self.assertIsNotNone(self.batch.started_at)

    def test_complete_production(self):
        """Test completing batch production."""
        self.batch.start_production()
        self.batch.complete_production(quantity_produced=900, quantity_rejected=100)
        self.assertEqual(self.batch.status, 'completed')
        self.assertEqual(self.batch.quantity_produced, 900)
        self.assertEqual(self.batch.quantity_rejected, 100)

    def test_yield_calculation(self):
        """Test yield percentage calculation."""
        self.batch.quantity_planned = 1000
        self.batch.quantity_produced = 900
        self.batch.save()
        self.assertEqual(self.batch.yield_percentage, 90.0)

    def test_submit_for_review(self):
        """Test submitting for review."""
        self.batch.start_production()
        self.batch.complete_production(900)
        self.batch.submit_for_review()
        self.assertEqual(self.batch.status, 'under_review')

    def test_release_batch(self):
        """Test releasing a batch."""
        self.batch.start_production()
        self.batch.complete_production(900)
        self.batch.release(self.user)
        self.assertEqual(self.batch.status, 'released')
        self.assertEqual(self.batch.released_by, self.user)
        self.assertIsNotNone(self.batch.release_date)

    def test_reject_batch(self):
        """Test rejecting a batch."""
        self.batch.start_production()
        self.batch.complete_production(900)
        self.batch.reject()
        self.assertEqual(self.batch.status, 'rejected')

    def test_quarantine_batch(self):
        """Test quarantining a batch."""
        self.batch.quarantine()
        self.assertEqual(self.batch.status, 'quarantined')


class BatchStepTestCase(TestCase):
    """Test cases for BatchStep model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.mbr = MasterBatchRecord.objects.create(
            title='Test MBR',
            product_name='Test Product',
            product_code='TP-001',
            created_by=self.user
        )
        self.batch = BatchRecord.objects.create(
            batch_number='BATCH-001',
            lot_number='LOT-001',
            mbr=self.mbr,
            quantity_planned=1000,
            created_by=self.user
        )
        self.step = BatchStep.objects.create(
            batch=self.batch,
            step_number=1,
            instruction_text='Mix ingredients',
            created_by=self.user
        )

    def test_batch_step_creation(self):
        """Test creating a batch step."""
        self.assertEqual(self.step.step_number, 1)
        self.assertEqual(self.step.status, 'pending')

    def test_start_step(self):
        """Test starting a batch step."""
        self.step.start_step(self.user)
        self.assertEqual(self.step.status, 'in_progress')
        self.assertEqual(self.step.operator, self.user)
        self.assertIsNotNone(self.step.started_at)

    def test_complete_step(self):
        """Test completing a batch step."""
        self.step.start_step(self.user)
        actual_values = {'temperature': 25, 'time': 30}
        self.step.complete_step(actual_values)
        self.assertEqual(self.step.status, 'completed')
        self.assertEqual(self.step.actual_values, actual_values)
        self.assertIsNotNone(self.step.operator_signed_at)

    def test_verify_step(self):
        """Test verifying a batch step."""
        self.step.start_step(self.user)
        self.step.complete_step({'temperature': 25})
        self.step.verify_step(self.user)
        self.assertEqual(self.step.verifier, self.user)
        self.assertIsNotNone(self.step.verifier_signed_at)

    def test_skip_step(self):
        """Test skipping a batch step."""
        self.step.skip_step()
        self.assertEqual(self.step.status, 'skipped')


class BatchDeviationTestCase(TestCase):
    """Test cases for BatchDeviation model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.mbr = MasterBatchRecord.objects.create(
            title='Test MBR',
            product_name='Test Product',
            product_code='TP-001',
            created_by=self.user
        )
        self.batch = BatchRecord.objects.create(
            batch_number='BATCH-001',
            lot_number='LOT-001',
            mbr=self.mbr,
            quantity_planned=1000,
            created_by=self.user
        )
        self.deviation = BatchDeviation.objects.create(
            batch=self.batch,
            deviation_type='parameter_excursion',
            description='Temperature exceeded 30C',
            created_by=self.user
        )

    def test_deviation_creation(self):
        """Test creating a batch deviation."""
        self.assertEqual(self.deviation.deviation_type, 'parameter_excursion')
        self.assertEqual(self.deviation.status, 'open')
        self.assertTrue(self.deviation.deviation_id.startswith('BD-'))

    def test_resolve_deviation(self):
        """Test resolving a deviation."""
        self.deviation.resolve(self.user)
        self.assertEqual(self.deviation.status, 'resolved')
        self.assertEqual(self.deviation.resolved_by, self.user)
        self.assertIsNotNone(self.deviation.resolution_date)

    def test_close_deviation(self):
        """Test closing a deviation."""
        self.deviation.resolve(self.user)
        self.deviation.close()
        self.assertEqual(self.deviation.status, 'closed')


class BatchMaterialTestCase(TestCase):
    """Test cases for BatchMaterial model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.mbr = MasterBatchRecord.objects.create(
            title='Test MBR',
            product_name='Test Product',
            product_code='TP-001',
            created_by=self.user
        )
        self.batch = BatchRecord.objects.create(
            batch_number='BATCH-001',
            lot_number='LOT-001',
            mbr=self.mbr,
            quantity_planned=1000,
            created_by=self.user
        )
        self.material = BatchMaterial.objects.create(
            batch=self.batch,
            material_name='Ingredient A',
            material_code='ING-A-001',
            lot_number='MAT-LOT-001',
            quantity_required=100,
            unit_of_measure='kg',
            created_by=self.user
        )

    def test_material_creation(self):
        """Test creating batch material."""
        self.assertEqual(self.material.material_code, 'ING-A-001')
        self.assertEqual(self.material.status, 'pending')

    def test_dispense_material(self):
        """Test dispensing material."""
        self.material.dispense(self.user)
        self.assertEqual(self.material.status, 'dispensed')
        self.assertEqual(self.material.dispensed_by, self.user)

    def test_verify_material(self):
        """Test verifying material."""
        self.material.dispense(self.user)
        self.material.verify(self.user)
        self.assertEqual(self.material.status, 'verified')
        self.assertEqual(self.material.verified_by, self.user)

    def test_consume_material(self):
        """Test consuming material."""
        self.material.dispense(self.user)
        self.material.verify(self.user)
        self.material.consume(95)
        self.assertEqual(self.material.status, 'consumed')
        self.assertEqual(self.material.quantity_used, 95)


class BatchEquipmentTestCase(TestCase):
    """Test cases for BatchEquipment model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.mbr = MasterBatchRecord.objects.create(
            title='Test MBR',
            product_name='Test Product',
            product_code='TP-001',
            created_by=self.user
        )
        self.batch = BatchRecord.objects.create(
            batch_number='BATCH-001',
            lot_number='LOT-001',
            mbr=self.mbr,
            quantity_planned=1000,
            created_by=self.user
        )
        self.equipment = BatchEquipment.objects.create(
            batch=self.batch,
            equipment_name='Mixer A',
            created_by=self.user
        )

    def test_equipment_creation(self):
        """Test creating batch equipment."""
        self.assertEqual(self.equipment.equipment_name, 'Mixer A')
        self.assertFalse(self.equipment.calibration_verified)
        self.assertFalse(self.equipment.cleaning_verified)

    def test_start_usage(self):
        """Test starting equipment usage."""
        self.equipment.start_usage()
        self.assertIsNotNone(self.equipment.usage_start)

    def test_end_usage(self):
        """Test ending equipment usage."""
        self.equipment.start_usage()
        self.equipment.end_usage()
        self.assertIsNotNone(self.equipment.usage_end)

    def test_verify_calibration(self):
        """Test verifying calibration."""
        self.equipment.verify_calibration(self.user)
        self.assertTrue(self.equipment.calibration_verified)
        self.assertEqual(self.equipment.verified_by, self.user)

    def test_verify_cleaning(self):
        """Test verifying cleaning."""
        self.equipment.verify_cleaning(self.user)
        self.assertTrue(self.equipment.cleaning_verified)
        self.assertEqual(self.equipment.verified_by, self.user)
