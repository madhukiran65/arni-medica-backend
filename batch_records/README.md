# Batch Records App

A comprehensive Django application for managing Electronic Batch Records (EBR) in pharmaceutical and medical device manufacturing environments. This app handles the complete lifecycle of batch production including master batch records, production batches, steps, deviations, materials, and equipment tracking.

## Features

- **Master Batch Records**: Define manufacturing processes and quality specifications
- **Batch Records**: Track actual production batches with full lifecycle management
- **Batch Steps**: Execute and verify individual production steps with data collection
- **Batch Deviations**: Document and track deviations from specifications
- **Batch Materials**: Track material usage and consumption
- **Batch Equipment**: Monitor equipment usage, calibration, and cleaning
- **Audit Trail**: Complete created_by/updated_by tracking via AuditedModel
- **Auto-ID Generation**: Automatic ID generation (MBR-0001, BR-0001, BD-0001)
- **Status Management**: Comprehensive state machines for all entities
- **REST API**: Full REST API with filtering, searching, and ordering
- **Django Admin**: Rich admin interface with inline editing and color-coded badges

## Installation

1. Add to INSTALLED_APPS in settings.py:
```python
INSTALLED_APPS = [
    ...
    'batch_records',
]
```

2. Include URLs in main urls.py:
```python
urlpatterns = [
    ...
    path('api/batch_records/', include('batch_records.urls')),
]
```

3. Run migrations:
```bash
python manage.py migrate batch_records
```

## Models

### MasterBatchRecord
Defines the manufacturing process and quality specifications for a batch of products.

**Fields:**
- `mbr_id` (CharField): Auto-generated ID (MBR-0001)
- `title` (CharField): Record title
- `product_name` (CharField): Name of the product
- `product_code` (CharField): Product identifier
- `version` (CharField): Version number (default: 1.0)
- `bill_of_materials` (JSONField): List of required materials
- `manufacturing_instructions` (JSONField): Step-by-step process
- `quality_specifications` (JSONField): Quality parameters
- `linked_document` (FK): Reference to Document model
- `product_line` (FK): Reference to ProductLine
- `effective_date` (DateField): When this record becomes effective
- `status` (CharField): draft, in_review, approved, superseded, obsolete
- `approved_by` (FK): User who approved the record
- `approval_date` (DateTimeField): When approval occurred

**Methods:**
- `approve(user)`: Approve the master batch record
- `supersede()`: Mark as superseded
- `obsolete()`: Mark as obsolete

### BatchRecord
Represents an actual manufacturing batch with production history and quality data.

**Fields:**
- `batch_id` (CharField): Auto-generated ID (BR-0001)
- `batch_number` (CharField): Unique batch identifier (unique)
- `lot_number` (CharField): Lot number
- `mbr` (FK): Reference to MasterBatchRecord (PROTECT)
- `quantity_planned` (IntegerField): Planned production quantity
- `quantity_produced` (IntegerField): Actual quantity produced
- `quantity_rejected` (IntegerField): Rejected quantity (default: 0)
- `yield_percentage` (DecimalField): Auto-calculated yield %
- `started_at` (DateTimeField): Production start time
- `completed_at` (DateTimeField): Production end time
- `status` (CharField): pending, in_progress, completed, under_review, released, rejected, quarantined
- `production_line` (CharField): Production line identifier
- `site` (FK): Reference to Site
- `reviewed_by` (FK): User who reviewed the batch
- `released_by` (FK): User who released the batch
- `release_date` (DateTimeField): Release timestamp
- `has_deviations` (BooleanField): Flag for deviations
- `review_by_exception` (BooleanField): RBE flag

**Methods:**
- `start_production()`: Start batch production
- `complete_production(quantity_produced, quantity_rejected)`: Complete production
- `submit_for_review()`: Submit for review
- `release(user)`: Release batch
- `reject()`: Reject batch
- `quarantine()`: Quarantine batch
- `update_deviation_flag()`: Update deviation status

### BatchStep
Individual steps within a batch production process.

**Fields:**
- `batch` (FK): Reference to BatchRecord
- `step_number` (IntegerField): Step sequence
- `instruction_text` (TextField): Step instructions
- `required_data_fields` (JSONField): Data fields to collect
- `actual_values` (JSONField): Collected data
- `specifications` (JSONField): Acceptable parameter ranges
- `status` (CharField): pending, in_progress, completed, skipped, deviated
- `requires_verification` (BooleanField): Verification requirement
- `operator` (FK): User performing the step
- `operator_signed_at` (DateTimeField): Operator signature time
- `verifier` (FK): User verifying the step
- `verifier_signed_at` (DateTimeField): Verifier signature time
- `deviation_notes` (TextField): Notes on deviations
- `started_at` (DateTimeField): Step start time
- `completed_at` (DateTimeField): Step completion time
- `is_within_spec` (BooleanField): Specification compliance

**Methods:**
- `start_step(operator)`: Start executing the step
- `complete_step(actual_values)`: Complete with data
- `verify_step(verifier)`: Verify completion
- `skip_step()`: Skip the step

**Unique Together:** (batch, step_number)

### BatchDeviation
Tracks deviations from specifications or procedures.

**Fields:**
- `deviation_id` (CharField): Auto-generated ID (BD-0001)
- `batch_step` (FK): Reference to BatchStep (nullable)
- `batch` (FK): Reference to BatchRecord
- `deviation_type` (CharField): parameter_excursion, equipment_failure, material_issue, process_deviation, documentation_error, environmental
- `description` (TextField): Deviation description
- `impact_assessment` (TextField): Impact assessment
- `immediate_action` (TextField): Immediate corrective action
- `root_cause` (TextField): Root cause analysis
- `linked_deviation` (FK): Reference to Deviation model
- `linked_capa` (FK): Reference to CAPA model
- `status` (CharField): open, investigating, resolved, closed
- `resolved_by` (FK): User who resolved
- `resolution_date` (DateTimeField): Resolution timestamp

**Methods:**
- `resolve(user)`: Mark as resolved
- `close()`: Close the deviation

### BatchMaterial
Tracks material usage and consumption.

**Fields:**
- `batch` (FK): Reference to BatchRecord
- `material_name` (CharField): Material name
- `material_code` (CharField): Material code
- `lot_number` (CharField): Material lot number
- `quantity_required` (DecimalField): Required quantity
- `quantity_used` (DecimalField): Actual quantity used
- `unit_of_measure` (CharField): Unit (kg, L, etc.)
- `status` (CharField): pending, dispensed, verified, consumed, returned
- `dispensed_by` (FK): User who dispensed
- `verified_by` (FK): User who verified

**Methods:**
- `dispense(user)`: Mark as dispensed
- `verify(user)`: Verify the material
- `consume(quantity_used)`: Mark as consumed

### BatchEquipment
Monitors equipment usage, calibration, and cleaning.

**Fields:**
- `batch` (FK): Reference to BatchRecord
- `equipment` (FK): Reference to Equipment model
- `equipment_name` (CharField): Equipment name
- `equipment_id_manual` (CharField): Manual equipment ID
- `usage_start` (DateTimeField): Usage start time
- `usage_end` (DateTimeField): Usage end time
- `calibration_verified` (BooleanField): Calibration status
- `cleaning_verified` (BooleanField): Cleaning status
- `verified_by` (FK): User who verified

**Methods:**
- `start_usage()`: Record usage start
- `end_usage()`: Record usage end
- `verify_calibration(user)`: Verify calibration
- `verify_cleaning(user)`: Verify cleaning

## API Endpoints

All endpoints require authentication (IsAuthenticated permission).

### Master Batch Records
- `GET /api/batch_records/master-batch-records/` - List all
- `POST /api/batch_records/master-batch-records/` - Create new
- `GET /api/batch_records/master-batch-records/{id}/` - Retrieve
- `PUT/PATCH /api/batch_records/master-batch-records/{id}/` - Update
- `DELETE /api/batch_records/master-batch-records/{id}/` - Delete
- `POST /api/batch_records/master-batch-records/{id}/approve/` - Approve
- `POST /api/batch_records/master-batch-records/{id}/supersede/` - Supersede
- `POST /api/batch_records/master-batch-records/{id}/obsolete/` - Mark obsolete

### Batch Records
- `GET /api/batch_records/batch-records/` - List all
- `POST /api/batch_records/batch-records/` - Create new
- `GET /api/batch_records/batch-records/{id}/` - Retrieve
- `PUT/PATCH /api/batch_records/batch-records/{id}/` - Update
- `DELETE /api/batch_records/batch-records/{id}/` - Delete
- `POST /api/batch_records/batch-records/{id}/start/` - Start production
- `POST /api/batch_records/batch-records/{id}/complete/` - Complete production
- `POST /api/batch_records/batch-records/{id}/submit_for_review/` - Submit for review
- `POST /api/batch_records/batch-records/{id}/release/` - Release batch
- `POST /api/batch_records/batch-records/{id}/reject/` - Reject batch
- `POST /api/batch_records/batch-records/{id}/quarantine/` - Quarantine batch

### Batch Steps
- `GET /api/batch_records/batch-steps/` - List all
- `POST /api/batch_records/batch-steps/` - Create new
- `GET /api/batch_records/batch-steps/{id}/` - Retrieve
- `PUT/PATCH /api/batch_records/batch-steps/{id}/` - Update
- `DELETE /api/batch_records/batch-steps/{id}/` - Delete
- `POST /api/batch_records/batch-steps/{id}/start/` - Start step
- `POST /api/batch_records/batch-steps/{id}/complete/` - Complete step
- `POST /api/batch_records/batch-steps/{id}/verify/` - Verify step
- `POST /api/batch_records/batch-steps/{id}/skip/` - Skip step

### Batch Deviations
- `GET /api/batch_records/batch-deviations/` - List all
- `POST /api/batch_records/batch-deviations/` - Create new
- `GET /api/batch_records/batch-deviations/{id}/` - Retrieve
- `PUT/PATCH /api/batch_records/batch-deviations/{id}/` - Update
- `DELETE /api/batch_records/batch-deviations/{id}/` - Delete
- `POST /api/batch_records/batch-deviations/{id}/resolve/` - Resolve
- `POST /api/batch_records/batch-deviations/{id}/close/` - Close

### Batch Materials
- `GET /api/batch_records/batch-materials/` - List all
- `POST /api/batch_records/batch-materials/` - Create new
- `GET /api/batch_records/batch-materials/{id}/` - Retrieve
- `PUT/PATCH /api/batch_records/batch-materials/{id}/` - Update
- `DELETE /api/batch_records/batch-materials/{id}/` - Delete
- `POST /api/batch_records/batch-materials/{id}/dispense/` - Dispense
- `POST /api/batch_records/batch-materials/{id}/verify/` - Verify
- `POST /api/batch_records/batch-materials/{id}/consume/` - Consume

### Batch Equipment
- `GET /api/batch_records/batch-equipment/` - List all
- `POST /api/batch_records/batch-equipment/` - Create new
- `GET /api/batch_records/batch-equipment/{id}/` - Retrieve
- `PUT/PATCH /api/batch_records/batch-equipment/{id}/` - Update
- `DELETE /api/batch_records/batch-equipment/{id}/` - Delete
- `POST /api/batch_records/batch-equipment/{id}/start_usage/` - Start usage
- `POST /api/batch_records/batch-equipment/{id}/end_usage/` - End usage
- `POST /api/batch_records/batch-equipment/{id}/verify_calibration/` - Verify calibration
- `POST /api/batch_records/batch-equipment/{id}/verify_cleaning/` - Verify cleaning

## Filtering, Searching & Ordering

All list endpoints support:

**Filter Examples:**
- `?status=approved` - Filter by status
- `?product_code=TP-001` - Filter by product code
- `?created_at__date__gte=2024-01-01` - Filter by date range

**Search Examples:**
- `?search=MBR-0001` - Search by ID
- `?search=Test Product` - Search by name

**Ordering Examples:**
- `?ordering=created_at` - Oldest first
- `?ordering=-created_at` - Newest first
- `?ordering=status,-created_at` - Multiple fields

## Serializers

### List Serializers
- `MasterBatchRecordListSerializer`
- `BatchRecordListSerializer`
- `BatchStepListSerializer`
- `BatchDeviationListSerializer`
- `BatchMaterialListSerializer`
- `BatchEquipmentListSerializer`

### Detail Serializers
- `MasterBatchRecordDetailSerializer`
- `BatchRecordDetailSerializer` (includes nested related objects)
- `BatchStepDetailSerializer`
- `BatchDeviationDetailSerializer`
- `BatchMaterialDetailSerializer`
- `BatchEquipmentDetailSerializer`

### Action Serializers
- `BatchRecordStartSerializer`
- `BatchRecordCompleteSerializer` - requires quantity_produced
- `BatchRecordReleaseSerializer`
- `BatchStepCompleteSerializer` - requires actual_values
- `BatchDeviationResolveSerializer`
- etc.

## Admin Interface

Rich Django admin interface with:
- Color-coded status badges
- Inline editing for related objects
- Links between related records
- Comprehensive filtering
- Search functionality
- Read-only audit fields
- Collapsed sections for detailed content

Access at: `/admin/batch_records/`

## Testing

Run tests with:
```bash
python manage.py test batch_records
```

Includes comprehensive test cases for:
- Model creation and field validation
- Auto-ID generation
- Status transitions
- Method functionality
- Data calculations (yield percentage)

## Dependencies

- Django (3.2+)
- Django REST Framework
- django-filter
- core.models.AuditedModel (from your project)

## Related Models

Requires the following models from other apps:
- `documents.Document`
- `users.ProductLine`
- `users.Site`
- `equipment.Equipment` (optional, FK nullable)
- `deviations.Deviation` (optional, FK nullable)
- `capa.CAPA` (optional, FK nullable)
- Django's built-in `User` model

## Status Workflows

### MasterBatchRecord States
```
draft → in_review → approved
                  ↘ superseded
                  ↘ obsolete
```

### BatchRecord States
```
pending → in_progress → completed → under_review → released
                       ↘           ↘ rejected
                        ↘ quarantined
```

### BatchStep States
```
pending → in_progress → completed
                      ↘ deviated
       ↘ skipped
```

### BatchDeviation States
```
open → investigating → resolved → closed
```

### BatchMaterial States
```
pending → dispensed → verified → consumed
                   ↘ returned
```

## Signals

Automatic signal handlers:
- Update batch `has_deviations` flag when deviations are saved/deleted
- Track creation and modification times via AuditedModel

## Production Notes

- All models inherit from `AuditedModel` for audit trail tracking
- Foreign keys use PROTECT/SET_NULL as appropriate for data integrity
- Auto-ID generation is sequential based on model instance count
- Unique constraints on natural identifiers (batch_number, mbr_id, etc.)
- Database indexes on frequently queried fields
- Comprehensive error handling with ValidationError
- JSON fields for flexible data structures
- Decimal fields for precise quantity calculations

## Future Enhancements

- Batch release approvals workflow
- Advanced analytics and reporting
- Integration with ERP systems
- Digital signature implementation
- Batch retest capabilities
- Stability monitoring
- Expiration date tracking
