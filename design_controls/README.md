# Design Controls App (DHF/DMR/DHR)

A comprehensive Django application for managing Design History File (DHF), Design and Master Record (DMR), and Design History Record (DHR) compliance documentation for medical device development.

## Overview

This app implements the FDA's design control requirements (21 CFR Part 11) and provides a structured approach to managing:

- **Design History File (DHF)**: Complete history of design decisions
- **Design and Master Record (DMR)**: Current approved design specifications
- **Design History Record (DHR)**: Record of all design changes and decisions

## Models

### 1. DesignProject
The main project container for design control activities.

**Fields:**
- `project_id`: Auto-generated unique identifier (DP-0001, DP-0002, etc.)
- `title`: Project name
- `description`: Project details
- `product_type`: device, ivd, combination, or drug_device
- `current_phase`: planning, design_input, design_output, verification, validation, transfer, production
- `project_lead`: FK to User
- `regulatory_pathway`: 510k, pma, de_novo, exempt, ce_mark, ivdr
- `target_completion_date`: Project deadline
- `status`: active, on_hold, completed, cancelled
- `department`: FK to Department (optional)
- `product_line`: FK to ProductLine (optional)

**Endpoints:**
- `GET/POST /api/design-controls/design-projects/`
- `GET/PUT/PATCH/DELETE /api/design-controls/design-projects/{id}/`
- `GET /api/design-controls/design-projects/{id}/traceability_report/` - Generate traceability report

### 2. UserNeed
Documents user/stakeholder requirements that drive design.

**Fields:**
- `need_id`: Auto-generated unique identifier (UN-0001, UN-0002, etc.)
- `project`: FK to DesignProject
- `description`: Requirement description
- `source`: clinical, marketing, regulatory, engineering, manufacturing, customer_feedback
- `priority`: critical, high, medium, low
- `acceptance_criteria`: How to verify the need is met
- `rationale`: Why this need exists
- `status`: draft, approved, superseded
- `approved_by`: FK to User (optional)

**Endpoints:**
- `GET/POST /api/design-controls/user-needs/`
- `GET/PUT/PATCH/DELETE /api/design-controls/user-needs/{id}/`

**Filters:**
- `project`, `source`, `priority`, `status`, `approved_by`
- Search: `need_id`, `description`

### 3. DesignInput
Specifications and acceptance criteria derived from user needs.

**Fields:**
- `input_id`: Auto-generated unique identifier (DI-0001, DI-0002, etc.)
- `project`: FK to DesignProject
- `specification`: The input requirement
- `measurable_criteria`: How to measure compliance
- `input_type`: functional, performance, safety, regulatory, environmental, interface, packaging
- `tolerance`: Acceptable variation range
- `test_method`: How to test the input
- `linked_user_needs`: M2M to UserNeed
- `status`: draft, approved, superseded
- `approved_by`: FK to User (optional)

**Endpoints:**
- `GET/POST /api/design-controls/design-inputs/`
- `GET/PUT/PATCH/DELETE /api/design-controls/design-inputs/{id}/`

**Filters:**
- `project`, `input_type`, `status`, `approved_by`
- Search: `input_id`, `specification`

### 4. DesignOutput
Drawings, specifications, software, and other design deliverables.

**Fields:**
- `output_id`: Auto-generated unique identifier (DO-0001, DO-0002, etc.)
- `project`: FK to DesignProject
- `description`: What the output delivers
- `output_type`: drawing, specification, software, formula, process, labeling
- `file`: FileField for attachments
- `revision`: Version number (e.g., 1.0, 2.1)
- `linked_inputs`: M2M to DesignInput
- `status`: draft, approved, superseded
- `approved_by`: FK to User (optional)

**Endpoints:**
- `GET/POST /api/design-controls/design-outputs/`
- `GET/PUT/PATCH/DELETE /api/design-controls/design-outputs/{id}/`

**Filters:**
- `project`, `output_type`, `status`, `approved_by`
- Search: `output_id`, `description`

### 5. VVProtocol
Verification and Validation protocols and results.

**Fields:**
- `protocol_id`: Auto-generated unique identifier (VV-0001, VV-0002, etc.)
- `project`: FK to DesignProject
- `title`: Protocol name
- `protocol_type`: verification, validation
- `test_method`: How the test will be performed
- `acceptance_criteria`: Pass/fail criteria
- `sample_size`: Number of samples to test
- `linked_inputs`: M2M to DesignInput
- `linked_outputs`: M2M to DesignOutput
- `status`: draft, approved, executed, failed, superseded
- `execution_date`: When the test was performed
- `result`: pass, fail, conditional, not_executed
- `result_summary`: Summary of results
- `deviations_noted`: Any test deviations
- `executed_by`: FK to User (optional)
- `approved_by`: FK to User (optional)
- `file`: Protocol document
- `result_file`: Test results document

**Endpoints:**
- `GET/POST /api/design-controls/vv-protocols/`
- `GET/PUT/PATCH/DELETE /api/design-controls/vv-protocols/{id}/`
- `POST /api/design-controls/vv-protocols/{id}/mark_executed/` - Mark protocol as executed

**Filters:**
- `project`, `protocol_type`, `status`, `result`, `executed_by`, `approved_by`
- Date range: `execution_date_from`, `execution_date_to`
- Search: `protocol_id`, `title`

### 6. DesignReview
Design review meetings and decisions at each phase.

**Fields:**
- `review_id`: Auto-generated unique identifier (DR-0001, DR-0002, etc.)
- `project`: FK to DesignProject
- `phase`: planning, design_input, design_output, verification, validation, transfer, production
- `review_date`: When the review was held
- `attendees`: M2M to User
- `agenda`: Review topics
- `minutes`: Meeting notes
- `action_items`: JSONField array of action items
- `outcome`: approved, conditional, rejected, deferred
- `conditions`: Required conditions for approval
- `follow_up_date`: When to follow up
- `status`: scheduled, completed, cancelled

**Endpoints:**
- `GET/POST /api/design-controls/design-reviews/`
- `GET/PUT/PATCH/DELETE /api/design-controls/design-reviews/{id}/`

**Filters:**
- `project`, `phase`, `status`, `outcome`
- Date range: `review_date_from`, `review_date_to`
- Search: `review_id`, `phase`

### 7. DesignTransfer
Transfer of design to manufacturing.

**Fields:**
- `transfer_id`: Auto-generated unique identifier (DT-0001, DT-0002, etc.)
- `project`: FK to DesignProject
- `description`: Transfer scope
- `transfer_checklist`: JSONField array of checklist items
- `manufacturing_site`: FK to Site (optional)
- `production_readiness_confirmed`: Boolean flag
- `confirmed_by`: FK to User (optional)
- `confirmed_date`: When confirmation occurred
- `linked_document`: FK to Document (optional)
- `status`: planned, in_progress, completed, cancelled

**Endpoints:**
- `GET/POST /api/design-controls/design-transfers/`
- `GET/PUT/PATCH/DELETE /api/design-controls/design-transfers/{id}/`

**Filters:**
- `project`, `status`, `manufacturing_site`, `production_readiness_confirmed`
- Search: `transfer_id`

### 8. TraceabilityLink
Maps relationships between requirements, designs, and verification activities.

**Fields:**
- `project`: FK to DesignProject
- `user_need`: FK to UserNeed (optional)
- `design_input`: FK to DesignInput (optional)
- `design_output`: FK to DesignOutput (optional)
- `vv_protocol`: FK to VVProtocol (optional)
- `link_status`: complete, partial, missing
- `gap_description`: Description of gaps
- `notes`: Additional notes

**Endpoints:**
- `GET/POST /api/design-controls/traceability-links/`
- `GET/PUT/PATCH/DELETE /api/design-controls/traceability-links/{id}/`

**Filters:**
- `project`, `link_status`, `user_need`, `design_input`, `design_output`, `vv_protocol`
- Search: none (use filters)

## API Integration

### Installation

1. Add to `INSTALLED_APPS` in settings.py:
```python
INSTALLED_APPS = [
    # ...
    'design_controls',
]
```

2. Include URLs in main urls.py:
```python
from django.urls import path, include

urlpatterns = [
    # ...
    path('api/design-controls/', include('design_controls.urls')),
]
```

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Example API Calls

**Create a Design Project:**
```bash
POST /api/design-controls/design-projects/
{
  "title": "Widget Pro Medical Device",
  "description": "Advanced diagnostic device for patient monitoring",
  "product_type": "device",
  "product_type": "device",
  "regulatory_pathway": "510k",
  "project_lead": 1
}
```

**Create a User Need:**
```bash
POST /api/design-controls/user-needs/
{
  "project": 1,
  "description": "Device must accurately measure temperature within 0.1°C",
  "source": "clinical",
  "priority": "critical",
  "acceptance_criteria": "Validated testing shows ±0.1°C accuracy",
  "rationale": "Clinical requirement for accurate diagnosis"
}
```

**Create Design Input:**
```bash
POST /api/design-controls/design-inputs/
{
  "project": 1,
  "specification": "Temperature sensor resolution: 0.01°C",
  "measurable_criteria": "Sensor output shows 0.01°C minimum change detection",
  "input_type": "performance",
  "tolerance": "±0.05°C",
  "test_method": "Calibrated test bath with reference thermometer",
  "linked_user_needs": [1]
}
```

**Query Traceability Report:**
```bash
GET /api/design-controls/design-projects/1/traceability_report/

Response:
{
  "project_id": "DP-0001",
  "total_links": 45,
  "complete_links": 40,
  "partial_links": 3,
  "missing_links": 2,
  "missing_details": [...]
}
```

## Auto-ID Generation

All models use auto-incrementing ID fields generated via the `save()` method:

- **DesignProject**: DP-0001, DP-0002, DP-0003, ...
- **UserNeed**: UN-0001, UN-0002, UN-0003, ...
- **DesignInput**: DI-0001, DI-0002, DI-0003, ...
- **DesignOutput**: DO-0001, DO-0002, DO-0003, ...
- **VVProtocol**: VV-0001, VV-0002, VV-0003, ...
- **DesignReview**: DR-0001, DR-0002, DR-0003, ...
- **DesignTransfer**: DT-0001, DT-0002, DT-0003, ...

IDs are generated automatically on first save. No manual assignment required.

## Audit Trail

All models inherit from `core.models.AuditedModel`, providing:
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update
- `created_by`: User who created the record
- `updated_by`: User who last updated the record

## Admin Interface

Full Django admin support with:
- List views with filtering and search
- Detailed change forms with fieldsets
- Read-only audit fields
- Many-to-many field management
- File upload support

Access at: `/admin/design_controls/`

## Filtering & Search

### FilterSet Features

All viewsets support:
- **Filtering**: Use query parameters like `?status=approved&project=1`
- **Searching**: Use `?search=DP-0001` for keyword search
- **Ordering**: Use `?ordering=-created_at` or `?ordering=status`

### Example Queries

```bash
# Get all approved design inputs
GET /api/design-controls/design-inputs/?status=approved

# Get all critical user needs
GET /api/design-controls/user-needs/?priority=critical

# Search for specific project
GET /api/design-controls/design-projects/?search=Widget

# Get V&V protocols ordered by execution date
GET /api/design-controls/vv-protocols/?ordering=execution_date

# Get failed validation tests
GET /api/design-controls/vv-protocols/?protocol_type=validation&result=fail

# Get missing traceability links
GET /api/design-controls/traceability-links/?link_status=missing
```

## Regulatory Compliance

This app is designed to support compliance with:

- **FDA 21 CFR Part 11**: Electronic Records; Electronic Signatures
- **21 CFR Part 820 (Device Master Record & Design History File)**: Quality System Regulation
- **IEC 62304**: Software lifecycle processes for medical devices
- **ISO 13485**: Medical devices - Quality management systems

## Best Practices

1. **Traceability**: Maintain M2M links between user needs, design inputs, outputs, and V&V protocols
2. **Approvals**: Require management sign-off for critical documents via the `approved_by` field
3. **Versioning**: Track design output revisions (1.0, 1.1, 2.0, etc.)
4. **Reviews**: Conduct design reviews at each phase with documented minutes
5. **Testing**: Execute all V&V protocols and document results
6. **Transfers**: Complete transfer checklist before production release

## File Structure

```
design_controls/
├── __init__.py
├── apps.py
├── models.py
├── serializers.py
├── views.py
├── urls.py
├── filters.py
├── admin.py
├── signals.py
└── README.md
```

## Troubleshooting

### Auto-ID Not Generating
Ensure models inherit from `AuditedModel` and `save()` is called properly.

### Traceability Links Not Showing
Use `get_design_context` endpoint or check `link_status` field for gaps.

### Upload Not Working
Ensure `MEDIA_ROOT` and `MEDIA_URL` are configured in Django settings.
