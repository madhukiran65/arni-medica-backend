# Design Controls App - Usage Examples

## Setup

First, ensure the app is properly installed:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'design_controls',
]
```

```python
# urls.py
urlpatterns = [
    path('api/design-controls/', include('design_controls.urls')),
    # ...
]
```

```bash
python manage.py makemigrations design_controls
python manage.py migrate design_controls
```

## Example Workflow: Medical Device Development

This example shows a complete workflow for developing a temperature monitoring device.

### 1. Create a Design Project

```bash
POST /api/design-controls/design-projects/

{
  "title": "TempMonitor Pro - Patient Monitoring Device",
  "description": "Wireless temperature monitoring device for clinical settings",
  "product_type": "device",
  "regulatory_pathway": "510k",
  "project_lead": 1,
  "target_completion_date": "2024-12-31",
  "department": 1,
  "product_line": 2
}

Response:
{
  "id": 1,
  "project_id": "DP-0001",
  "title": "TempMonitor Pro - Patient Monitoring Device",
  "status": "active",
  "current_phase": "planning",
  "created_at": "2024-02-26T10:00:00Z",
  "updated_at": "2024-02-26T10:00:00Z"
}
```

### 2. Define User Needs

```bash
POST /api/design-controls/user-needs/

{
  "project": 1,
  "description": "Device must measure temperature accurately within clinical diagnostic ranges",
  "source": "clinical",
  "priority": "critical",
  "acceptance_criteria": "Validated testing demonstrates accuracy within ±0.1°C",
  "rationale": "Essential for accurate patient diagnosis and treatment decisions"
}

Response:
{
  "id": 1,
  "need_id": "UN-0001",
  "project": 1,
  "source": "clinical",
  "priority": "critical",
  "status": "draft"
}
```

```bash
POST /api/design-controls/user-needs/

{
  "project": 1,
  "description": "Device must wireless transmit data to hospital monitoring system",
  "source": "clinical",
  "priority": "critical",
  "acceptance_criteria": "Data transmits reliably with less than 0.1% loss rate",
  "rationale": "Enables real-time patient monitoring at nursing station"
}

Response:
{
  "id": 2,
  "need_id": "UN-0002",
  ...
}
```

```bash
POST /api/design-controls/user-needs/

{
  "project": 1,
  "description": "Device must operate for 48 hours on single charge",
  "source": "engineering",
  "priority": "high",
  "acceptance_criteria": "Battery test shows minimum 48-hour runtime",
  "rationale": "Reduces need for frequent charging in clinical environment"
}

Response:
{
  "id": 3,
  "need_id": "UN-0003",
  ...
}
```

### 3. Create Design Inputs

```bash
POST /api/design-controls/design-inputs/

{
  "project": 1,
  "specification": "Temperature sensor type: NTC Thermistor with accuracy rated to 0.05°C",
  "measurable_criteria": "Sensor output drift less than 0.02°C over 12-month period",
  "input_type": "performance",
  "tolerance": "±0.05°C",
  "test_method": "Calibrated temperature bath with NIST-traceable reference",
  "linked_user_needs": [1]
}

Response:
{
  "id": 1,
  "input_id": "DI-0001",
  ...
}
```

```bash
POST /api/design-controls/design-inputs/

{
  "project": 1,
  "specification": "Wireless transceiver: 2.4GHz IEEE 802.15.4 compliant module",
  "measurable_criteria": "Range minimum 50 meters, data packet loss less than 0.1%",
  "input_type": "functional",
  "test_method": "Open field testing at various distances and through obstacles",
  "linked_user_needs": [2]
}

Response:
{
  "id": 2,
  "input_id": "DI-0002",
  ...
}
```

```bash
POST /api/design-controls/design-inputs/

{
  "project": 1,
  "specification": "Battery capacity: 5000 mAh Li-Po with integrated charge controller",
  "measurable_criteria": "Continuous operation: minimum 48 hours at 1-minute reporting interval",
  "input_type": "performance",
  "tolerance": "±5% capacity variance",
  "test_method": "Continuous device operation with data logging every minute",
  "linked_user_needs": [3]
}

Response:
{
  "id": 3,
  "input_id": "DI-0003",
  ...
}
```

### 4. Create Design Outputs

```bash
POST /api/design-controls/design-outputs/

{
  "project": 1,
  "description": "PCB Schematic showing temperature sensor circuitry and signal conditioning",
  "output_type": "drawing",
  "revision": "1.0",
  "linked_inputs": [1]
}

Response:
{
  "id": 1,
  "output_id": "DO-0001",
  "revision": "1.0"
}
```

```bash
POST /api/design-controls/design-outputs/

{
  "project": 1,
  "description": "Wireless Protocol Specification detailing IEEE 802.15.4 implementation",
  "output_type": "specification",
  "revision": "1.0",
  "linked_inputs": [2]
}

Response:
{
  "id": 2,
  "output_id": "DO-0002",
  ...
}
```

### 5. Approve Design Inputs & Outputs

```bash
PATCH /api/design-controls/design-inputs/1/

{
  "status": "approved",
  "approved_by": 1
}

Response:
{
  "id": 1,
  "input_id": "DI-0001",
  "status": "approved",
  "approved_by": {
    "id": 1,
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### 6. Create Verification Protocol

```bash
POST /api/design-controls/vv-protocols/

{
  "project": 1,
  "title": "Temperature Sensor Accuracy Verification Test",
  "protocol_type": "verification",
  "test_method": "Device placed in calibrated temperature baths at 20°C, 37°C, and 42°C. Reading recorded after stabilization.",
  "acceptance_criteria": "All readings within ±0.1°C of reference temperature",
  "sample_size": 10,
  "linked_inputs": [1],
  "linked_outputs": [1]
}

Response:
{
  "id": 1,
  "protocol_id": "VV-0001",
  "status": "draft",
  "result": "not_executed"
}
```

```bash
POST /api/design-controls/vv-protocols/

{
  "project": 1,
  "title": "Wireless Range and Data Integrity Validation Test",
  "protocol_type": "validation",
  "test_method": "Transmit 1000 data packets at various distances (10m, 25m, 50m, 100m). Count successful receipts.",
  "acceptance_criteria": "At least 99.9% packet delivery rate at 50m range",
  "sample_size": 5,
  "linked_inputs": [2],
  "linked_outputs": [2]
}

Response:
{
  "id": 2,
  "protocol_id": "VV-0002",
  ...
}
```

### 7. Execute V&V Protocol

```bash
PATCH /api/design-controls/vv-protocols/1/

{
  "status": "executed",
  "execution_date": "2024-03-15",
  "result": "pass",
  "result_summary": "All 10 samples passed with readings within ±0.08°C at all three temperatures",
  "executed_by": 2
}

Response:
{
  "id": 1,
  "protocol_id": "VV-0001",
  "status": "executed",
  "result": "pass",
  "execution_date": "2024-03-15",
  "executed_by": {
    "id": 2,
    "username": "jane_test",
    "first_name": "Jane",
    "last_name": "Test"
  }
}
```

Or use the dedicated action:

```bash
POST /api/design-controls/vv-protocols/1/mark_executed/

{
  "execution_date": "2024-03-15",
  "result": "pass",
  "result_summary": "All 10 samples passed with readings within ±0.08°C"
}
```

### 8. Conduct Design Review

```bash
POST /api/design-controls/design-reviews/

{
  "project": 1,
  "phase": "design_output",
  "review_date": "2024-03-20",
  "attendees": [1, 2, 3, 4],
  "agenda": "Review design outputs, verification results, and readiness for validation",
  "minutes": "Team reviewed all design outputs. Verification tests passed successfully. Approved to proceed with validation phase.",
  "action_items": [
    {
      "item": "Complete wireless range validation testing",
      "assigned_to": "jane_test",
      "due_date": "2024-04-05"
    },
    {
      "item": "Update product labeling per regulatory feedback",
      "assigned_to": "john_doe",
      "due_date": "2024-04-10"
    }
  ],
  "outcome": "approved"
}

Response:
{
  "id": 1,
  "review_id": "DR-0001",
  "phase": "design_output",
  "status": "scheduled",
  "outcome": "approved"
}
```

### 9. Update Project Phase

```bash
PATCH /api/design-controls/design-projects/1/

{
  "current_phase": "validation"
}

Response:
{
  "id": 1,
  "project_id": "DP-0001",
  "current_phase": "validation",
  "status": "active"
}
```

### 10. Create Traceability Link

```bash
POST /api/design-controls/traceability-links/

{
  "project": 1,
  "user_need": 1,
  "design_input": 1,
  "design_output": 1,
  "vv_protocol": 1,
  "link_status": "complete",
  "notes": "Temperature measurement requirement fully traced from user need through output to verification"
}

Response:
{
  "id": 1,
  "project": 1,
  "user_need": 1,
  "design_input": 1,
  "design_output": 1,
  "vv_protocol": 1,
  "link_status": "complete"
}
```

### 11. Generate Traceability Report

```bash
GET /api/design-controls/design-projects/1/traceability_report/

Response:
{
  "project_id": "DP-0001",
  "total_links": 3,
  "complete_links": 3,
  "partial_links": 0,
  "missing_links": 0,
  "missing_details": []
}
```

### 12. Create Design Transfer

```bash
POST /api/design-controls/design-transfers/

{
  "project": 1,
  "description": "Transfer of TempMonitor Pro design to manufacturing partner XYZ Medical",
  "manufacturing_site": 1,
  "transfer_checklist": [
    {
      "item": "All design outputs finalized and approved",
      "completed": true
    },
    {
      "item": "Manufacturing documentation prepared",
      "completed": true
    },
    {
      "item": "Quality procedures established",
      "completed": true
    },
    {
      "item": "Manufacturing trial run completed",
      "completed": false,
      "due_date": "2024-05-01"
    }
  ],
  "status": "planned"
}

Response:
{
  "id": 1,
  "transfer_id": "DT-0001",
  "status": "planned"
}
```

### 13. Complete Manufacturing Transfer

```bash
PATCH /api/design-controls/design-transfers/1/

{
  "status": "in_progress",
  "transfer_checklist": [
    {
      "item": "All design outputs finalized and approved",
      "completed": true
    },
    {
      "item": "Manufacturing documentation prepared",
      "completed": true
    },
    {
      "item": "Quality procedures established",
      "completed": true
    },
    {
      "item": "Manufacturing trial run completed",
      "completed": true
    }
  ]
}

PATCH /api/design-controls/design-transfers/1/

{
  "status": "completed",
  "production_readiness_confirmed": true,
  "confirmed_by": 1,
  "confirmed_date": "2024-05-01"
}

Response:
{
  "id": 1,
  "transfer_id": "DT-0001",
  "status": "completed",
  "production_readiness_confirmed": true,
  "confirmed_date": "2024-05-01"
}
```

## Filtering Examples

### Get all critical user needs

```bash
GET /api/design-controls/user-needs/?priority=critical

Response:
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "need_id": "UN-0001",
      "priority": "critical",
      ...
    },
    {
      "id": 2,
      "need_id": "UN-0002",
      "priority": "critical",
      ...
    }
  ]
}
```

### Get all approved design inputs

```bash
GET /api/design-controls/design-inputs/?status=approved
```

### Get all passed V&V protocols

```bash
GET /api/design-controls/vv-protocols/?result=pass&protocol_type=verification
```

### Get all design reviews with conditions

```bash
GET /api/design-controls/design-reviews/?project=1&outcome=conditional
```

### Search by ID

```bash
GET /api/design-controls/design-projects/?search=DP-0001
```

### Get missing traceability links for a project

```bash
GET /api/design-controls/traceability-links/?project=1&link_status=missing
```

### Pagination

```bash
GET /api/design-controls/design-projects/?page=2&page_size=10
```

## Django Admin Examples

Access the Django admin interface at `/admin/design_controls/`

### Add a new Design Project in Admin

1. Navigate to `/admin/design_controls/designproject/`
2. Click "Add Design Project"
3. Fill in:
   - Title: "TempMonitor Pro"
   - Description: "Wireless temperature monitoring device"
   - Product Type: "device"
   - Regulatory Pathway: "510k"
   - Project Lead: Select from dropdown
4. Click "Save"

### Filter in Admin

- Click "Filter" on the right sidebar
- Select filters like Status, Current Phase, Product Type, Regulatory Pathway
- Results update automatically

### Search in Admin

- Use the search box at the top
- Search by: project_id, title, description
- Results display matching records

### Bulk Actions

- Check boxes next to records
- Select action from dropdown (when available)
- Click "Go"

## Advanced Usage

### Using the API with Python Requests

```python
import requests
import json

# Create a new user need
headers = {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
}

data = {
    "project": 1,
    "description": "Device must be sterilizable via autoclaving",
    "source": "regulatory",
    "priority": "high",
    "acceptance_criteria": "Device materials withstand 121°C, 15 min autoclave cycle",
    "rationale": "FDA requirement for reusable medical devices"
}

response = requests.post(
    'http://api.example.com/api/design-controls/user-needs/',
    json=data,
    headers=headers
)

print(response.json())
```

### Querying with Filters and Search

```python
# Get all design inputs for a project
response = requests.get(
    'http://api.example.com/api/design-controls/design-inputs/?project=1',
    headers=headers
)

# Get all high-priority needs
response = requests.get(
    'http://api.example.com/api/design-controls/user-needs/?priority=high',
    headers=headers
)

# Search for specific project
response = requests.get(
    'http://api.example.com/api/design-controls/design-projects/?search=DP-0001',
    headers=headers
)

# Get V&V protocols ordered by execution date
response = requests.get(
    'http://api.example.com/api/design-controls/vv-protocols/?ordering=execution_date',
    headers=headers
)
```

This comprehensive example demonstrates the complete workflow for managing design controls throughout the medical device development lifecycle.
