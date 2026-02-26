# Batch Records API Examples

Quick reference examples for using the Batch Records API.

## Authentication

All endpoints require authentication. Include the token in your request header:

```bash
curl -H "Authorization: Token YOUR_TOKEN" \
     https://api.example.com/api/batch_records/batch-records/
```

## Master Batch Record Examples

### Create a Master Batch Record

```bash
curl -X POST https://api.example.com/api/batch_records/master-batch-records/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Standard Manufacturing Process",
    "product_name": "Injectable Solution A",
    "product_code": "PROD-InjA-001",
    "version": "1.0",
    "bill_of_materials": [
      {"ingredient": "Active Pharma", "quantity": 100, "unit": "mg"},
      {"ingredient": "Excipient B", "quantity": 500, "unit": "mg"}
    ],
    "manufacturing_instructions": [
      {"step": 1, "instruction": "Dissolve API in solvent"},
      {"step": 2, "instruction": "Add excipients"}
    ],
    "quality_specifications": {
      "pH": {"min": 6.5, "max": 7.5},
      "Appearance": "Clear, colorless solution"
    },
    "product_line": 1,
    "effective_date": "2024-03-01"
  }'
```

### List Master Batch Records

```bash
# All records
curl https://api.example.com/api/batch_records/master-batch-records/ \
  -H "Authorization: Token YOUR_TOKEN"

# Filter by status
curl "https://api.example.com/api/batch_records/master-batch-records/?status=approved" \
  -H "Authorization: Token YOUR_TOKEN"

# Search by product code
curl "https://api.example.com/api/batch_records/master-batch-records/?search=PROD-InjA" \
  -H "Authorization: Token YOUR_TOKEN"

# Order by creation date (newest first)
curl "https://api.example.com/api/batch_records/master-batch-records/?ordering=-created_at" \
  -H "Authorization: Token YOUR_TOKEN"
```

### Retrieve a Master Batch Record

```bash
curl https://api.example.com/api/batch_records/master-batch-records/1/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Approve a Master Batch Record

```bash
curl -X POST https://api.example.com/api/batch_records/master-batch-records/1/approve/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Supersede a Master Batch Record

```bash
curl -X POST https://api.example.com/api/batch_records/master-batch-records/1/supersede/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Batch Record Examples

### Create a Batch Record

```bash
curl -X POST https://api.example.com/api/batch_records/batch-records/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "batch_number": "BATCH-2024-001",
    "lot_number": "LOT-20240226-001",
    "mbr": 1,
    "quantity_planned": 10000,
    "production_line": "Line A",
    "site": 1
  }'
```

### Start Batch Production

```bash
curl -X POST https://api.example.com/api/batch_records/batch-records/1/start/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'

# Response includes updated batch with started_at timestamp
```

### Complete Batch Production

```bash
curl -X POST https://api.example.com/api/batch_records/batch-records/1/complete/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity_produced": 9500,
    "quantity_rejected": 500
  }'
```

### Submit for Review

```bash
curl -X POST https://api.example.com/api/batch_records/batch-records/1/submit_for_review/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Release Batch

```bash
curl -X POST https://api.example.com/api/batch_records/batch-records/1/release/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### List Batch Records with Filters

```bash
# All batches in progress
curl "https://api.example.com/api/batch_records/batch-records/?status=in_progress" \
  -H "Authorization: Token YOUR_TOKEN"

# Batches with deviations
curl "https://api.example.com/api/batch_records/batch-records/?has_deviations=true" \
  -H "Authorization: Token YOUR_TOKEN"

# Batches from specific site
curl "https://api.example.com/api/batch_records/batch-records/?site=1" \
  -H "Authorization: Token YOUR_TOKEN"

# Batches completed in date range
curl "https://api.example.com/api/batch_records/batch-records/?completed_at__gte=2024-02-01&completed_at__lte=2024-02-28" \
  -H "Authorization: Token YOUR_TOKEN"
```

### Quarantine Batch

```bash
curl -X POST https://api.example.com/api/batch_records/batch-records/1/quarantine/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Batch Step Examples

### Create a Batch Step

```bash
curl -X POST https://api.example.com/api/batch_records/batch-steps/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "batch": 1,
    "step_number": 1,
    "instruction_text": "Mix ingredients in reactor for 30 minutes",
    "required_data_fields": ["temperature", "time", "rpm"],
    "specifications": {
      "temperature": {"min": 20, "max": 25},
      "rpm": {"min": 100, "max": 150}
    },
    "requires_verification": true
  }'
```

### Start a Batch Step

```bash
curl -X POST https://api.example.com/api/batch_records/batch-steps/1/start/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Complete a Batch Step

```bash
curl -X POST https://api.example.com/api/batch_records/batch-steps/1/complete/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "actual_values": {
      "temperature": 22.5,
      "time": 30,
      "rpm": 120
    }
  }'
```

### Verify a Batch Step

```bash
curl -X POST https://api.example.com/api/batch_records/batch-steps/1/verify/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Batch Deviation Examples

### Create a Deviation

```bash
curl -X POST https://api.example.com/api/batch_records/batch-deviations/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "batch": 1,
    "batch_step": 2,
    "deviation_type": "parameter_excursion",
    "description": "Temperature exceeded 30°C during mixing step",
    "impact_assessment": "Potential impact on product stability",
    "immediate_action": "Halted process, cooled reactor, initiated investigation"
  }'
```

### Resolve a Deviation

```bash
curl -X POST https://api.example.com/api/batch_records/batch-deviations/1/resolve/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "root_cause": "Temperature sensor malfunction",
    "immediate_action": "Replaced temperature sensor"
  }'
```

### Close a Deviation

```bash
curl -X POST https://api.example.com/api/batch_records/batch-deviations/1/close/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### List Deviations for a Batch

```bash
curl "https://api.example.com/api/batch_records/batch-deviations/?batch=1" \
  -H "Authorization: Token YOUR_TOKEN"
```

## Batch Material Examples

### Add Material to Batch

```bash
curl -X POST https://api.example.com/api/batch_records/batch-materials/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "batch": 1,
    "material_name": "Active Pharmaceutical Ingredient A",
    "material_code": "API-A-001",
    "lot_number": "LOT-API-202402-001",
    "quantity_required": 1000.000,
    "unit_of_measure": "mg"
  }'
```

### Dispense Material

```bash
curl -X POST https://api.example.com/api/batch_records/batch-materials/1/dispense/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Verify Material

```bash
curl -X POST https://api.example.com/api/batch_records/batch-materials/1/verify/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Consume Material

```bash
curl -X POST https://api.example.com/api/batch_records/batch-materials/1/consume/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity_used": 995.500
  }'
```

### List Materials for a Batch

```bash
curl "https://api.example.com/api/batch_records/batch-materials/?batch=1" \
  -H "Authorization: Token YOUR_TOKEN"
```

## Batch Equipment Examples

### Add Equipment to Batch

```bash
curl -X POST https://api.example.com/api/batch_records/batch-equipment/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "batch": 1,
    "equipment": 5,
    "equipment_name": "Reactor Vessel A",
    "equipment_id_manual": "REV-A-001"
  }'
```

### Start Equipment Usage

```bash
curl -X POST https://api.example.com/api/batch_records/batch-equipment/1/start_usage/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### End Equipment Usage

```bash
curl -X POST https://api.example.com/api/batch_records/batch-equipment/1/end_usage/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Verify Equipment Calibration

```bash
curl -X POST https://api.example.com/api/batch_records/batch-equipment/1/verify_calibration/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Verify Equipment Cleaning

```bash
curl -X POST https://api.example.com/api/batch_records/batch-equipment/1/verify_cleaning/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Common Query Parameters

### Filtering
```
?status=approved
?product_code__icontains=PROD
?created_at__date__gte=2024-02-01
?created_at__date__lte=2024-02-28
?site=1
?has_deviations=true
```

### Searching
```
?search=MBR-0001
?search=BATCH-2024
?search=Injectable
```

### Ordering
```
?ordering=created_at              # Oldest first
?ordering=-created_at             # Newest first
?ordering=status,-created_at      # Multiple fields
```

### Pagination (if enabled)
```
?limit=20&offset=0
?page=1
```

## Response Status Codes

- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Missing/invalid authentication
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `409 Conflict` - Invalid state transition
- `500 Server Error` - Server error

## Error Response Example

```json
{
  "detail": "Only pending batches can be started."
}
```

## Batch Status Workflow Example

```
1. Create batch (status: pending)
   POST /batch-records/

2. Start production (status: in_progress)
   POST /batch-records/1/start/

3. Add materials, steps, equipment
   POST /batch-materials/
   POST /batch-steps/

4. Complete production (status: completed)
   POST /batch-records/1/complete/

5. Submit for review (status: under_review)
   POST /batch-records/1/submit_for_review/

6. Release batch (status: released)
   POST /batch-records/1/release/
```

## Integration Example (Python)

```python
import requests
from django.conf import settings

BASE_URL = "https://api.example.com/api/batch_records"
TOKEN = "your_authentication_token"
HEADERS = {"Authorization": f"Token {TOKEN}"}

# Create a batch
response = requests.post(
    f"{BASE_URL}/batch-records/",
    headers=HEADERS,
    json={
        "batch_number": "BATCH-2024-001",
        "lot_number": "LOT-20240226-001",
        "mbr": 1,
        "quantity_planned": 10000,
        "production_line": "Line A",
        "site": 1
    }
)
batch = response.json()
batch_id = batch["id"]

# Start production
requests.post(
    f"{BASE_URL}/batch-records/{batch_id}/start/",
    headers=HEADERS,
    json={}
)

# Add materials
requests.post(
    f"{BASE_URL}/batch-materials/",
    headers=HEADERS,
    json={
        "batch": batch_id,
        "material_name": "API",
        "material_code": "API-001",
        "lot_number": "LOT-API-001",
        "quantity_required": 1000,
        "unit_of_measure": "mg"
    }
)

# Complete production
requests.post(
    f"{BASE_URL}/batch-records/{batch_id}/complete/",
    headers=HEADERS,
    json={
        "quantity_produced": 9500,
        "quantity_rejected": 500
    }
)
```
