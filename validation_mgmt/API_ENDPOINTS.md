# Validation Management API Endpoints Reference

## Base URL
```
/api/validation/
```

## Endpoints Overview

### 1. Validation Plans
Base: `/api/validation/validation-plans/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all plans (filterable, paginated) |
| POST | `/` | Create new plan |
| GET | `/{id}/` | Get plan details |
| PUT | `/{id}/` | Update plan |
| PATCH | `/{id}/` | Partial update |
| DELETE | `/{id}/` | Delete plan |
| POST | `/{id}/approve/` | Approve plan |
| POST | `/{id}/start_execution/` | Start execution |
| POST | `/{id}/complete/` | Mark completed |
| GET | `/{id}/summary/` | Get plan summary stats |

**Query Parameters (Filters):**
```
?title=<string>                    # Contains search
?system_name=<string>              # Contains search
?status=draft|approved|...         # Exact match
?validation_approach=traditional_csv|risk_based_csa|hybrid
?responsible_person=<user_id>
?qa_reviewer=<user_id>
?department=<dept_id>
?created_after=<datetime>
?created_before=<datetime>
?ordering=-created_at              # or +created_at, plan_id, status
```

**Example Request:**
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/validation/validation-plans/?status=approved&ordering=-created_at"
```

---

### 2. Validation Protocols
Base: `/api/validation/validation-protocols/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all protocols (filterable) |
| POST | `/` | Create new protocol |
| GET | `/{id}/` | Get protocol details |
| PUT | `/{id}/` | Update protocol |
| PATCH | `/{id}/` | Partial update |
| DELETE | `/{id}/` | Delete protocol |
| POST | `/{id}/approve/` | Approve protocol |
| POST | `/{id}/start_execution/` | Start execution |
| POST | `/{id}/complete_execution/` | Complete with result |

**Query Parameters (Filters):**
```
?title=<string>                    # Contains search
?protocol_type=iq|oq|pq|uat|...
?status=draft|approved|in_execution|completed|failed
?result=pass|fail|pass_with_deviations|not_executed
?plan=<plan_id>
?executed_by=<user_id>
?reviewed_by=<user_id>
?execution_after=<date>
?execution_before=<date>
```

**Complete Execution Request Body:**
```json
{
  "result": "pass",
  "result_summary": "All tests passed successfully"
}
```

---

### 3. Test Cases
Base: `/api/validation/test-cases/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all test cases |
| POST | `/` | Create new test case |
| GET | `/{id}/` | Get test case details |
| PUT | `/{id}/` | Update test case |
| PATCH | `/{id}/` | Partial update |
| DELETE | `/{id}/` | Delete test case |
| POST | `/{id}/execute/` | Mark as executed |

**Query Parameters (Filters):**
```
?title=<string>
?test_type=functional|negative|boundary|security|performance|usability
?status=not_executed|pass|fail|blocked|deferred
?priority=critical|high|medium|low
?protocol=<protocol_id>
?executed_by=<user_id>
?execution_after=<datetime>
?execution_before=<datetime>
```

**Execute Test Case Request Body:**
```json
{
  "status": "pass",
  "actual_result": "Test executed successfully, all assertions passed"
}
```

---

### 4. RTM Entries
Base: `/api/validation/rtm-entries/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all RTM entries |
| POST | `/` | Create new entry |
| GET | `/{id}/` | Get RTM entry details |
| PUT | `/{id}/` | Update entry |
| PATCH | `/{id}/` | Partial update |
| DELETE | `/{id}/` | Delete entry |
| POST | `/{id}/verify/` | Update verification status |
| GET | `/verification_summary/` | Get aggregate stats |

**Query Parameters (Filters):**
```
?requirement_id=<string>           # Contains search
?requirement_category=functional|performance|security|regulatory|usability|interface
?verification_status=not_verified|verified|partially_verified|failed
?plan=<plan_id>
?linked_protocol=<protocol_id>
```

**Verify RTM Entry Request Body:**
```json
{
  "verification_status": "verified"
}
```

**Verification Summary Query:**
```
GET /verification_summary/?plan_id=<plan_id>

Response:
{
  "total_requirements": 25,
  "verified": 20,
  "not_verified": 3,
  "partially_verified": 2,
  "failed": 0,
  "verification_percentage": 80.0
}
```

---

### 5. Deviations
Base: `/api/validation/deviations/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all deviations |
| POST | `/` | Create new deviation |
| GET | `/{id}/` | Get deviation details |
| PUT | `/{id}/` | Update deviation |
| PATCH | `/{id}/` | Partial update |
| DELETE | `/{id}/` | Delete deviation |
| POST | `/{id}/resolve/` | Resolve deviation |
| GET | `/summary_by_severity/` | Get severity breakdown |

**Query Parameters (Filters):**
```
?severity=critical|major|minor|cosmetic
?status=open|investigating|resolved|closed
?resolution_type=fix_and_retest|risk_accepted|deferred|workaround
?protocol=<protocol_id>
?test_case=<test_case_id>
?resolved_by=<user_id>
?resolution_after=<datetime>
?resolution_before=<datetime>
```

**Resolve Deviation Request Body:**
```json
{
  "resolution": "Database connection pooling was implemented",
  "resolution_type": "fix_and_retest"
}
```

**Severity Summary Query:**
```
GET /summary_by_severity/?plan_id=<plan_id>

Response:
{
  "critical": 0,
  "major": 2,
  "minor": 5,
  "cosmetic": 1,
  "total": 8,
  "open": 2,
  "resolved": 6
}
```

---

### 6. Summary Reports
Base: `/api/validation/summary-reports/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all reports |
| POST | `/` | Create new report |
| GET | `/{id}/` | Get report details |
| PUT | `/{id}/` | Update report |
| PATCH | `/{id}/` | Partial update |
| DELETE | `/{id}/` | Delete report |
| POST | `/{id}/approve/` | Approve report |
| POST | `/{id}/move_to_review/` | Move to review |

**Query Parameters (Filters):**
```
?title=<string>                    # Contains search
?overall_conclusion=validated|not_validated|conditionally_validated
?status=draft|in_review|approved
?plan=<plan_id>
?approved_by=<user_id>
?approval_after=<datetime>
?approval_before=<datetime>
```

---

## Response Formats

### List Response (Pagination)
```json
{
  "count": 42,
  "next": "http://localhost:8000/api/validation/validation-plans/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "plan_id": "VP-0001",
      "title": "HR System Validation",
      "system_name": "HR System",
      "system_version": "2.1.0",
      "status": "approved",
      "responsible_person": 5,
      "responsible_person_name": "John Smith",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Detail Response
```json
{
  "id": 1,
  "plan_id": "VP-0001",
  "title": "HR System Validation",
  "system_name": "HR System",
  "system_version": "2.1.0",
  "description": "Complete validation of HR system...",
  "scope": "All modules except payroll",
  "risk_assessment_summary": "Medium risk, legacy system",
  "validation_approach": "traditional_csv",
  "status": "approved",
  "responsible_person": 5,
  "responsible_person_name": "John Smith",
  "qa_reviewer": 8,
  "qa_reviewer_name": "Jane Doe",
  "department": 2,
  "department_name": "IT Operations",
  "approval_date": "2024-01-15T10:30:00Z",
  "target_completion": "2024-04-30",
  "protocol_count": 3,
  "rtm_entry_count": 45,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

## Common Query Patterns

### Get Draft Plans Assigned to User 5
```
GET /validation/validation-plans/?status=draft&responsible_person=5
```

### Get Failed Protocols from Plan 1
```
GET /validation/validation-protocols/?plan=1&result=fail
```

### Get Critical Deviations Not Yet Resolved
```
GET /validation/deviations/?severity=critical&status=open
```

### Get Test Cases for Protocol 3 That Failed
```
GET /validation/test-cases/?protocol=3&status=fail
```

### Get Verification Summary for Plan 1
```
GET /validation/rtm-entries/verification_summary/?plan_id=1
```

### Get Deviations by Severity for Plan 1
```
GET /validation/deviations/summary_by_severity/?plan_id=1
```

---

## Authentication

All endpoints require authentication. Include the bearer token in headers:

```bash
curl -H "Authorization: Bearer <your_token>" \
  http://localhost:8000/api/validation/validation-plans/
```

---

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 400 Bad Request
```json
{
  "error": "Only draft plans can be approved"
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

## Pagination

Default page size: 20 items

Change page: `?page=2`
Change size: `?page_size=50`

---

## Ordering

Default: `-created_at` (newest first)

Available fields: `created_at`, `updated_at`, `plan_id`, `status`, etc. (model-specific)

Use `-` prefix for descending: `?ordering=-created_at`

---

## File Uploads

For endpoints accepting file uploads (protocol_file, result_file, evidence_file):

```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -F "protocol_file=@/path/to/file.pdf" \
  http://localhost:8000/api/validation/validation-protocols/1/
```
