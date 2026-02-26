# Validation Management (CSV/CSA) Django App

## Overview

Complete production-ready Django application for managing Computerized System Validation (CSV) and Computerized System Audit (CSA) activities. The app provides comprehensive tools for validation planning, protocol execution, test case management, requirements traceability, deviation tracking, and reporting.

## Project Structure

```
validation_mgmt/
├── __init__.py                 # App initialization
├── apps.py                     # App configuration
├── models.py                   # 6 models with auto-ID generation
├── serializers.py              # List & Detail serializers for all models
├── views.py                    # ModelViewSet with filtering & actions
├── urls.py                     # DefaultRouter URL configuration
├── admin.py                    # Django admin interface
└── IMPLEMENTATION.md           # This file
```

## Models

All models inherit from `core.models.AuditedModel` which provides `created_by`, `updated_by`, `created_at`, and `updated_at` fields automatically.

### 1. ValidationPlan
Master validation plan for CSV/CSA activities.

**Fields:**
- `plan_id` (CharField, auto-generated "VP-0001"): Unique identifier
- `title` (CharField): Plan title
- `system_name` (CharField): Target system name
- `system_version` (CharField): System version
- `description` (TextField): Detailed plan description
- `scope` (TextField): Validation scope
- `risk_assessment_summary` (TextField, optional): Risk analysis summary
- `validation_approach` (CharField, choices):
  - 'traditional_csv': Traditional CSV
  - 'risk_based_csa': Risk-Based CSA
  - 'hybrid': Hybrid approach
- `responsible_person` (ForeignKey to User): Primary responsible person
- `qa_reviewer` (ForeignKey to User, optional): QA reviewer
- `status` (CharField, choices):
  - 'draft': Initial state
  - 'approved': Ready for execution
  - 'in_execution': Currently executing
  - 'completed': Execution finished
  - 'closed': Finalized
- `approval_date` (DateTimeField, optional): When plan was approved
- `target_completion` (DateField, optional): Expected completion date
- `department` (ForeignKey to users.Department, optional): Related department

**Auto-ID Generation:**
Auto-generates plan_id in save() method: VP-0001, VP-0002, etc.

---

### 2. ValidationProtocol
Individual validation protocols (IQ, OQ, PQ, UAT, Regression, Security).

**Fields:**
- `protocol_id` (CharField, auto-generated "VPROT-0001"): Unique identifier
- `plan` (ForeignKey to ValidationPlan): Parent validation plan
- `title` (CharField): Protocol title
- `protocol_type` (CharField, choices):
  - 'iq': Installation Qualification
  - 'oq': Operational Qualification
  - 'pq': Performance Qualification
  - 'uat': User Acceptance Testing
  - 'regression': Regression Testing
  - 'security': Security Testing
- `description` (TextField): Protocol description
- `prerequisites` (JSONField, default=[]): List of prerequisites
- `test_environment` (CharField): Environment where tests run
- `test_cases` (JSONField, default=[]): List of associated test case references
- `total_test_cases` (IntegerField, default=0): Total count
- `passed_test_cases` (IntegerField, default=0): Passed count
- `failed_test_cases` (IntegerField, default=0): Failed count
- `execution_date` (DateField, optional): When protocol was executed
- `result` (CharField, choices):
  - 'pass': All tests passed
  - 'fail': Tests failed
  - 'pass_with_deviations': Passed but with deviations
  - 'not_executed': Not yet executed
- `result_summary` (TextField, optional): Summary of results
- `deviations_noted` (TextField, optional): Deviations description
- `executed_by` (ForeignKey to User, optional): Who executed
- `reviewed_by` (ForeignKey to User, optional): Who reviewed
- `approved_by` (ForeignKey to User, optional): Who approved
- `status` (CharField, choices):
  - 'draft': Initial state
  - 'approved': Ready for execution
  - 'in_execution': Currently executing
  - 'completed': Execution finished
  - 'failed': Execution failed
- `protocol_file` (FileField, optional): Protocol document
- `result_file` (FileField, optional): Result document

**Auto-ID Generation:**
Auto-generates protocol_id in save() method: VPROT-0001, VPROT-0002, etc.

---

### 3. ValidationTestCase
Individual test cases within protocols.

**Fields:**
- `test_case_id` (CharField, auto-generated "TC-0001"): Unique identifier
- `protocol` (ForeignKey to ValidationProtocol): Parent protocol
- `title` (CharField): Test case title
- `description` (TextField): Detailed description
- `test_type` (CharField, choices):
  - 'functional': Functional testing
  - 'negative': Negative testing
  - 'boundary': Boundary value testing
  - 'security': Security testing
  - 'performance': Performance testing
  - 'usability': Usability testing
- `preconditions` (TextField, optional): Prerequisites to run test
- `test_steps` (JSONField, default=[]): List of test steps
- `expected_result` (TextField): Expected outcome
- `actual_result` (TextField, optional): What actually happened
- `status` (CharField, choices):
  - 'not_executed': Not yet run
  - 'pass': Test passed
  - 'fail': Test failed
  - 'blocked': Cannot execute (blocker)
  - 'deferred': Postponed
- `priority` (CharField, choices):
  - 'critical': Must pass
  - 'high': Very important
  - 'medium': Standard
  - 'low': Nice to have
- `executed_by` (ForeignKey to User, optional): Who executed
- `execution_date` (DateTimeField, optional): When executed
- `evidence_file` (FileField, optional): Evidence/screenshot
- `notes` (TextField, optional): Additional notes

**Auto-ID Generation:**
Auto-generates test_case_id in save() method: TC-0001, TC-0002, etc.

---

### 4. RTMEntry
Requirements Traceability Matrix entries linking requirements to test cases.

**Fields:**
- `rtm_id` (CharField, auto-generated "RTM-0001"): Unique identifier
- `plan` (ForeignKey to ValidationPlan): Parent plan
- `requirement_id` (CharField): External requirement identifier
- `requirement_text` (TextField): Full requirement description
- `requirement_source` (CharField): Where requirement came from
- `requirement_category` (CharField, choices):
  - 'functional': Functional requirement
  - 'performance': Performance requirement
  - 'security': Security requirement
  - 'regulatory': Regulatory requirement
  - 'usability': Usability requirement
  - 'interface': Interface requirement
- `linked_test_cases` (ManyToManyField to ValidationTestCase): Covering tests
- `linked_protocol` (ForeignKey to ValidationProtocol, optional): Primary protocol
- `verification_status` (CharField, choices):
  - 'not_verified': No verification yet
  - 'verified': Requirement verified
  - 'partially_verified': Partially verified
  - 'failed': Verification failed
- `gap_description` (TextField, optional): Description of gaps
- `notes` (TextField, optional): Additional notes

**Auto-ID Generation:**
Auto-generates rtm_id in save() method: RTM-0001, RTM-0002, etc.

---

### 5. ValidationDeviation
Deviations found during validation execution.

**Fields:**
- `deviation_id` (CharField, auto-generated "VD-0001"): Unique identifier
- `protocol` (ForeignKey to ValidationProtocol): Associated protocol
- `test_case` (ForeignKey to ValidationTestCase, optional): Associated test case
- `description` (TextField): What deviated
- `severity` (CharField, choices):
  - 'critical': System failure risk
  - 'major': Significant impact
  - 'minor': Minor impact
  - 'cosmetic': Appearance only
- `impact_assessment` (TextField): Impact analysis
- `resolution` (TextField, optional): How it was resolved
- `resolution_type` (CharField, choices):
  - 'fix_and_retest': Code fix required
  - 'risk_accepted': Risk accepted without fix
  - 'deferred': Addressed in future release
  - 'workaround': Workaround provided
- `status` (CharField, choices):
  - 'open': Newly created
  - 'investigating': Under investigation
  - 'resolved': Resolution implemented
  - 'closed': Approved and closed
- `resolved_by` (ForeignKey to User, optional): Who resolved
- `resolution_date` (DateTimeField, optional): When resolved
- `linked_deviation` (ForeignKey to deviations.Deviation, optional): Link to system deviations

**Auto-ID Generation:**
Auto-generates deviation_id in save() method: VD-0001, VD-0002, etc.

---

### 6. ValidationSummaryReport
Comprehensive validation summary report.

**Fields:**
- `report_id` (CharField, auto-generated "VSR-0001"): Unique identifier
- `plan` (OneToOneField to ValidationPlan): Associated plan (unique)
- `title` (CharField): Report title
- `iq_status` (CharField, choices):
  - 'pass': IQ passed
  - 'fail': IQ failed
  - 'not_applicable': N/A
  - 'not_executed': Not run
- `oq_status` (CharField, same choices as iq_status)
- `pq_status` (CharField, same choices as iq_status)
- `overall_test_count` (IntegerField, default=0): Total tests
- `overall_pass_count` (IntegerField, default=0): Passed tests
- `overall_fail_count` (IntegerField, default=0): Failed tests
- `deviations_count` (IntegerField, default=0): Total deviations
- `open_deviations_count` (IntegerField, default=0): Open deviations
- `overall_conclusion` (CharField, choices):
  - 'validated': System is validated
  - 'not_validated': System not validated
  - 'conditionally_validated': Validated with conditions
- `executive_summary` (TextField): High-level summary
- `recommendations` (TextField): Recommendations
- `status` (CharField, choices):
  - 'draft': In preparation
  - 'in_review': Under review
  - 'approved': Finalized
- `approved_by` (ForeignKey to User, optional): Who approved
- `approval_date` (DateTimeField, optional): When approved
- `linked_document` (ForeignKey to documents.Document, optional): Linked document

**Auto-ID Generation:**
Auto-generates report_id in save() method: VSR-0001, VSR-0002, etc.

---

## Serializers

### List Serializers
Minimal representations for list views:
- `ValidationPlanListSerializer`
- `ValidationProtocolListSerializer`
- `ValidationTestCaseListSerializer`
- `RTMEntryListSerializer`
- `ValidationDeviationListSerializer`
- `ValidationSummaryReportListSerializer`

### Detail Serializers
Full representations for detail views:
- `ValidationPlanDetailSerializer`
- `ValidationProtocolDetailSerializer`
- `ValidationTestCaseDetailSerializer`
- `RTMEntryDetailSerializer`
- `ValidationDeviationDetailSerializer`
- `ValidationSummaryReportDetailSerializer`

**Features:**
- Nested relationships for detail views
- Read-only computed fields (counts, related names)
- User name resolution (get_full_name)
- Proper field selection for each context

---

## Views (ViewSets)

All ViewSets use:
- **Permission:** `IsAuthenticated` - User must be logged in
- **Router:** `DefaultRouter` - Full CRUD + custom actions
- **Filtering:** `DjangoFilterBackend` with custom `FilterSet` per model
- **Ordering:** Support for `created_at`, `updated_at`, and model-specific fields
- **Serialization:** Automatic List/Detail switching based on action

### ValidationPlanViewSet
**Endpoints:**
- `GET /api/validation-plans/` - List with filtering
- `POST /api/validation-plans/` - Create
- `GET /api/validation-plans/{id}/` - Retrieve
- `PUT /api/validation-plans/{id}/` - Update
- `PATCH /api/validation-plans/{id}/` - Partial update
- `DELETE /api/validation-plans/{id}/` - Delete

**Custom Actions:**
- `POST /api/validation-plans/{id}/approve/` - Approve plan
- `POST /api/validation-plans/{id}/start_execution/` - Begin execution
- `POST /api/validation-plans/{id}/complete/` - Mark completed
- `GET /api/validation-plans/{id}/summary/` - Get statistics

**Filter Fields:**
- `title` (contains search)
- `system_name` (contains search)
- `status` (exact)
- `validation_approach` (exact)
- `responsible_person` (user ID)
- `qa_reviewer` (user ID)
- `department` (department ID)
- `created_after`, `created_before` (date range)

---

### ValidationProtocolViewSet
**Endpoints:** Standard CRUD + custom actions
- `POST /api/validation-protocols/{id}/approve/` - Approve protocol
- `POST /api/validation-protocols/{id}/start_execution/` - Begin execution
- `POST /api/validation-protocols/{id}/complete_execution/` - Complete with result

**Filter Fields:**
- `title` (contains search)
- `protocol_type` (exact)
- `status` (exact)
- `result` (exact)
- `plan` (plan ID)
- `executed_by` (user ID)
- `reviewed_by` (user ID)
- `execution_after`, `execution_before` (date range)

---

### ValidationTestCaseViewSet
**Endpoints:** Standard CRUD + custom actions
- `POST /api/test-cases/{id}/execute/` - Mark test case as executed

**Filter Fields:**
- `title` (contains search)
- `test_type` (exact)
- `status` (exact)
- `priority` (exact)
- `protocol` (protocol ID)
- `executed_by` (user ID)
- `execution_after`, `execution_before` (datetime range)

---

### RTMEntryViewSet
**Endpoints:** Standard CRUD + custom actions
- `POST /api/rtm-entries/{id}/verify/` - Update verification status
- `GET /api/rtm-entries/verification_summary/` - Get aggregate verification stats

**Filter Fields:**
- `requirement_id` (contains search)
- `requirement_category` (exact)
- `verification_status` (exact)
- `plan` (plan ID)
- `linked_protocol` (protocol ID)

---

### ValidationDeviationViewSet
**Endpoints:** Standard CRUD + custom actions
- `POST /api/deviations/{id}/resolve/` - Mark deviation as resolved
- `GET /api/deviations/summary_by_severity/` - Get severity breakdown

**Filter Fields:**
- `severity` (exact)
- `status` (exact)
- `resolution_type` (exact)
- `protocol` (protocol ID)
- `test_case` (test case ID)
- `resolved_by` (user ID)
- `resolution_after`, `resolution_before` (datetime range)

---

### ValidationSummaryReportViewSet
**Endpoints:** Standard CRUD + custom actions
- `POST /api/summary-reports/{id}/approve/` - Approve report
- `POST /api/summary-reports/{id}/move_to_review/` - Move to review

**Filter Fields:**
- `title` (contains search)
- `overall_conclusion` (exact)
- `status` (exact)
- `plan` (plan ID)
- `approved_by` (user ID)
- `approval_after`, `approval_before` (datetime range)

---

## URL Configuration

### DefaultRouter Registration
The app uses Django REST Framework's `DefaultRouter` which automatically provides:
- Browsable API endpoints
- `.json` format support
- Auto-generated trailing slashes
- Pagination support

### URL Patterns
```
/api/validation-plans/                    - ValidationPlanViewSet
/api/validation-protocols/                - ValidationProtocolViewSet
/api/test-cases/                          - ValidationTestCaseViewSet
/api/rtm-entries/                         - RTMEntryViewSet
/api/deviations/                          - ValidationDeviationViewSet
/api/summary-reports/                     - ValidationSummaryReportViewSet
```

### Integration
Add to main `urls.py`:
```python
from django.urls import path, include

urlpatterns = [
    path('api/validation/', include('validation_mgmt.urls')),
]
```

---

## Admin Interface

Fully configured Django admin with:

### ValidationPlanAdmin
- List display: plan_id, title, system_name, status, validation_approach, responsible_person, target_completion
- Filters: status, validation_approach, created_at, updated_at, department
- Search: plan_id, title, system_name, description
- Fieldsets: Identification, Description, Validation Configuration, Assignments, Status and Dates, Audit

### ValidationProtocolAdmin
- List display: protocol_id, title, protocol_type, plan, status, result, total_test_cases, passed_test_cases
- Filters: protocol_type, status, result, execution_date, created_at
- Search: protocol_id, title, description, plan__title
- Fieldsets: Identification, Description, Test Cases, Execution, Results, Files, Audit

### ValidationTestCaseAdmin
- List display: test_case_id, title, protocol, test_type, priority, status, executed_by
- Filters: test_type, priority, status, execution_date, created_at
- Search: test_case_id, title, description, protocol__title
- Fieldsets: Identification, Description, Test Details, Execution, Evidence, Audit

### RTMEntryAdmin
- List display: rtm_id, requirement_id, plan, requirement_category, verification_status
- Filters: requirement_category, verification_status, created_at
- Search: rtm_id, requirement_id, requirement_text, plan__title
- Fieldsets: Identification, Requirement Details, Verification, Notes, Audit
- Filter horizontal: linked_test_cases

### ValidationDeviationAdmin
- List display: deviation_id, protocol, severity, status, resolution_type, resolved_by
- Filters: severity, status, resolution_type, resolution_date, created_at
- Search: deviation_id, description, protocol__title
- Fieldsets: Identification, Description, Resolution, Linking, Audit

### ValidationSummaryReportAdmin
- List display: report_id, title, plan, overall_conclusion, status, approved_by
- Filters: overall_conclusion, status, iq_status, oq_status, pq_status, approval_date, created_at
- Search: report_id, title, executive_summary, plan__title
- Fieldsets: Identification, Qualification Status, Test Statistics, Deviations, Conclusion, Approval, Linking, Audit

---

## Installation & Setup

### 1. Add to INSTALLED_APPS
```python
INSTALLED_APPS = [
    ...
    'validation_mgmt.apps.ValidationMgmtConfig',
]
```

### 2. Configure Django REST Framework
```python
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

### 3. Include URLs in main project
```python
# urls.py
from django.urls import path, include

urlpatterns = [
    path('api/validation/', include('validation_mgmt.urls')),
]
```

### 4. Run Migrations
```bash
python manage.py makemigrations validation_mgmt
python manage.py migrate validation_mgmt
```

### 5. Create Superuser & Access Admin
```bash
python manage.py createsuperuser
# Access at /admin/
```

---

## Features

### Auto-ID Generation
All models generate unique IDs automatically using the save() method:
- ValidationPlan: VP-0001, VP-0002, ...
- ValidationProtocol: VPROT-0001, VPROT-0002, ...
- ValidationTestCase: TC-0001, TC-0002, ...
- RTMEntry: RTM-0001, RTM-0002, ...
- ValidationDeviation: VD-0001, VD-0002, ...
- ValidationSummaryReport: VSR-0001, VSR-0002, ...

### Tuple-Based Choices
All choice fields use Python tuples:
```python
CHOICES = (
    ('value', 'Display Name'),
    ('value', 'Display Name'),
)
```

### Filtering & Search
All endpoints support filtering via query parameters:
```
/api/validation-plans/?status=approved&system_name=HR%20System&created_after=2024-01-01
```

### Workflow Actions
Custom actions for status transitions:
- Approve plans/protocols
- Start/complete execution
- Execute test cases
- Resolve deviations
- Approve reports

### Relationships
- One-to-many: ValidationPlan → Protocols, RTMEntries, Deviations
- Many-to-many: RTMEntry ↔ ValidationTestCases
- One-to-one: ValidationPlan ↔ ValidationSummaryReport

### Audit Trail
All models inherit created_by, updated_by, created_at, updated_at from AuditedModel

---

## Production Considerations

1. **File Storage:** Configure Django file storage backend for protocol_file, result_file, evidence_file
2. **Permissions:** Implement custom permission classes if needed (e.g., IsProjectOwner)
3. **Pagination:** Default 20 items/page, configure as needed
4. **Caching:** Consider caching summary endpoints
5. **Logging:** Use Django logging for audit trail
6. **Notifications:** Add signals for status transitions
7. **Exports:** Implement CSV/PDF export for reports
8. **Concurrency:** Use select_for_update() if needed for high-concurrency scenarios

---

## Testing

All ViewSets are testable with:
```python
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User

class ValidationPlanTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@test.com', 'pass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_plans(self):
        response = self.client.get('/api/validation/validation-plans/')
        self.assertEqual(response.status_code, 200)
```

---

## Summary

This is a production-ready Django validation management app providing:
- 6 interconnected models for CSV/CSA validation management
- Complete REST API with filtering, ordering, and custom actions
- Django admin interface for administrative tasks
- Automatic ID generation
- Audit trail through AuditedModel inheritance
- Comprehensive serialization with nested relationships
- Type-safe choice fields using tuples

All code follows Django best practices and is ready for immediate production deployment.
