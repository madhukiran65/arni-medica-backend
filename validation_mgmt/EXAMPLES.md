# Validation Management - Usage Examples

## Setup & Installation

### 1. Add to settings.py

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'django_filters',

    # Project apps
    'core',
    'users',
    'documents',
    'deviations',
    'validation_mgmt',  # Add here
]

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

### 2. Update urls.py

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('rest_framework.urls')),
    path('api/validation/', include('validation_mgmt.urls')),
]
```

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## Example Workflows

### Workflow 1: Complete CSV Validation Process

#### Step 1: Create Validation Plan

```python
# Python script or Django shell
from django.contrib.auth.models import User
from users.models import Department
from validation_mgmt.models import ValidationPlan

# Get or create users and department
qa_user = User.objects.get(username='john_doe')
reviewer_user = User.objects.get(username='jane_smith')
dept = Department.objects.get(name='IT Operations')

# Create plan
plan = ValidationPlan.objects.create(
    title='HR System v2.1 - Complete CSV',
    system_name='Human Resources Management System',
    system_version='2.1.0',
    description='Comprehensive validation of HR system migration',
    scope='All modules: Payroll, Attendance, Leave Management, Reports',
    risk_assessment_summary='Medium-High risk due to legacy system integration',
    validation_approach='traditional_csv',
    responsible_person=qa_user,
    qa_reviewer=reviewer_user,
    department=dept,
    target_completion='2024-12-31',
)

print(f"Created plan: {plan.plan_id} - {plan.title}")
# Output: Created plan: VP-0001 - HR System v2.1 - Complete CSV
```

#### Step 2: Create Validation Protocols

```python
from validation_mgmt.models import ValidationProtocol

# Create IQ Protocol
iq_protocol = ValidationProtocol.objects.create(
    plan=plan,
    title='Installation Qualification - HR System',
    protocol_type='iq',
    description='Verify correct installation and configuration',
    test_environment='Staging Environment',
    prerequisites=['Database backup created', 'Network connectivity verified'],
    status='draft',
)

# Create OQ Protocol
oq_protocol = ValidationProtocol.objects.create(
    plan=plan,
    title='Operational Qualification - HR System',
    protocol_type='oq',
    description='Verify system operates within defined parameters',
    test_environment='Staging Environment',
    prerequisites=['IQ completed and passed'],
    status='draft',
)

# Create PQ Protocol
pq_protocol = ValidationProtocol.objects.create(
    plan=plan,
    title='Performance Qualification - HR System',
    protocol_type='pq',
    description='Verify system performance meets requirements',
    test_environment='Production-like Environment',
    prerequisites=['OQ completed and passed'],
    status='draft',
)

print(f"Created protocols: {iq_protocol.protocol_id}, {oq_protocol.protocol_id}, {pq_protocol.protocol_id}")
```

#### Step 3: Create Test Cases

```python
from validation_mgmt.models import ValidationTestCase

# IQ Test Cases
test_case_1 = ValidationTestCase.objects.create(
    protocol=iq_protocol,
    title='Database Connection Test',
    description='Verify database connection is established',
    test_type='functional',
    preconditions='Database server is running',
    test_steps=['1. Open application', '2. Check connection status', '3. Query sample data'],
    expected_result='Database connection successful, query returns data',
    priority='critical',
)

test_case_2 = ValidationTestCase.objects.create(
    protocol=iq_protocol,
    title='User Login Functionality',
    description='Verify user can login to system',
    test_type='functional',
    preconditions='User account exists in system',
    test_steps=['1. Navigate to login page', '2. Enter credentials', '3. Click submit'],
    expected_result='User logged in successfully, dashboard displayed',
    priority='critical',
)

# OQ Test Cases
test_case_3 = ValidationTestCase.objects.create(
    protocol=oq_protocol,
    title='Payroll Calculation Accuracy',
    description='Verify payroll calculations are accurate',
    test_type='functional',
    test_steps=['1. Enter employee data', '2. Run payroll calculation', '3. Compare with expected'],
    expected_result='Calculated amounts match expected values within 0.01%',
    priority='high',
)

# PQ Test Cases
test_case_4 = ValidationTestCase.objects.create(
    protocol=pq_protocol,
    title='System Performance Under Load',
    description='Verify system handles peak load',
    test_type='performance',
    test_steps=['1. Simulate 1000 concurrent users', '2. Monitor response times', '3. Check system stability'],
    expected_result='Average response time < 2 seconds, system remains stable',
    priority='critical',
)

print(f"Created {ValidationTestCase.objects.filter(protocol__plan=plan).count()} test cases")
```

#### Step 4: Create RTM Entries

```python
from validation_mgmt.models import RTMEntry

# Create requirements
req1 = RTMEntry.objects.create(
    plan=plan,
    requirement_id='REQ-001',
    requirement_text='System shall have database connectivity',
    requirement_source='Technical Specifications v2.1',
    requirement_category='functional',
    linked_protocol=iq_protocol,
)
req1.linked_test_cases.add(test_case_1)

req2 = RTMEntry.objects.create(
    plan=plan,
    requirement_id='REQ-002',
    requirement_text='System shall authenticate users securely',
    requirement_source='Security Requirements',
    requirement_category='security',
    linked_protocol=iq_protocol,
)
req2.linked_test_cases.add(test_case_2)

req3 = RTMEntry.objects.create(
    plan=plan,
    requirement_id='REQ-003',
    requirement_text='Payroll calculations must be accurate within 0.01%',
    requirement_source='Business Requirements',
    requirement_category='functional',
    linked_protocol=oq_protocol,
)
req3.linked_test_cases.add(test_case_3)

print(f"Created {RTMEntry.objects.filter(plan=plan).count()} requirements")
```

#### Step 5: Approve Plans

```python
from django.utils import timezone

# Approve plan
plan.status = 'approved'
plan.approval_date = timezone.now()
plan.save()

# Approve protocols
for protocol in plan.protocols.all():
    protocol.status = 'approved'
    protocol.approved_by = reviewer_user
    protocol.save()

print("All plans and protocols approved")
```

#### Step 6: Execute Test Cases

```python
from django.utils import timezone

# Execute IQ test cases
test_case_1.status = 'pass'
test_case_1.actual_result = 'Database connection successful'
test_case_1.executed_by = qa_user
test_case_1.execution_date = timezone.now()
test_case_1.save()

test_case_2.status = 'pass'
test_case_2.actual_result = 'User authenticated and dashboard displayed'
test_case_2.executed_by = qa_user
test_case_2.execution_date = timezone.now()
test_case_2.save()

# Update protocol stats
iq_protocol.total_test_cases = 2
iq_protocol.passed_test_cases = 2
iq_protocol.failed_test_cases = 0
iq_protocol.save()

print("Test cases executed")
```

#### Step 7: Create Deviation (if needed)

```python
from validation_mgmt.models import ValidationDeviation

deviation = ValidationDeviation.objects.create(
    protocol=oq_protocol,
    test_case=test_case_3,
    description='Payroll calculation shows 0.02% variance from expected',
    severity='major',
    impact_assessment='Potential financial impact on employee compensation',
    status='investigating',
)

print(f"Created deviation: {deviation.deviation_id}")
```

#### Step 8: Resolve Deviation

```python
from django.utils import timezone

deviation.status = 'resolved'
deviation.resolution = 'Decimal precision increased in calculation engine'
deviation.resolution_type = 'fix_and_retest'
deviation.resolved_by = qa_user
deviation.resolution_date = timezone.now()
deviation.save()

print("Deviation resolved")
```

#### Step 9: Verify RTM Entries

```python
for rtm in plan.rtm_entries.all():
    rtm.verification_status = 'verified'
    rtm.save()

print("All requirements verified")
```

#### Step 10: Create Summary Report

```python
from validation_mgmt.models import ValidationSummaryReport

report = ValidationSummaryReport.objects.create(
    plan=plan,
    title='HR System v2.1 - Validation Summary Report',
    iq_status='pass',
    oq_status='pass_with_deviations',
    pq_status='pass',
    overall_test_count=4,
    overall_pass_count=3,
    overall_fail_count=0,
    deviations_count=1,
    open_deviations_count=0,
    overall_conclusion='conditionally_validated',
    executive_summary='System is validated with one resolved deviation regarding payroll precision',
    recommendations='Deploy to production with continued monitoring of payroll calculations',
    status='draft',
    approved_by=reviewer_user,
    approval_date=timezone.now(),
)

report.status = 'approved'
report.save()

print(f"Created and approved report: {report.report_id}")
```

---

### Workflow 2: API-Based Plan Creation

```bash
# 1. Get authentication token
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "password"}'

# Response:
# {"token": "abc123xyz..."}

TOKEN="abc123xyz..."

# 2. Create validation plan
curl -X POST http://localhost:8000/api/validation/validation-plans/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New System Validation",
    "system_name": "New ERP System",
    "system_version": "1.0.0",
    "description": "Complete validation of new ERP implementation",
    "scope": "Accounting, Inventory, Purchasing",
    "validation_approach": "risk_based_csa",
    "responsible_person": 5,
    "qa_reviewer": 8,
    "department": 2,
    "target_completion": "2024-06-30"
  }'

# Response:
# {
#   "id": 2,
#   "plan_id": "VP-0002",
#   "title": "New System Validation",
#   ...
# }
```

---

### Workflow 3: Filter & Retrieve Data

```bash
TOKEN="abc123xyz..."

# Get all draft plans
curl -H "Authorization: Token $TOKEN" \
  "http://localhost:8000/api/validation/validation-plans/?status=draft"

# Get approved protocols for plan 1
curl -H "Authorization: Token $TOKEN" \
  "http://localhost:8000/api/validation/validation-protocols/?plan=1&status=approved"

# Get failed test cases
curl -H "Authorization: Token $TOKEN" \
  "http://localhost:8000/api/validation/test-cases/?status=fail"

# Get critical deviations
curl -H "Authorization: Token $TOKEN" \
  "http://localhost:8000/api/validation/deviations/?severity=critical"

# Get requirement verification summary
curl -H "Authorization: Token $TOKEN" \
  "http://localhost:8000/api/validation/rtm-entries/verification_summary/?plan_id=1"

# Response:
# {
#   "total_requirements": 45,
#   "verified": 40,
#   "not_verified": 3,
#   "partially_verified": 2,
#   "failed": 0,
#   "verification_percentage": 88.89
# }
```

---

## Admin Interface Usage

### Accessing Admin
1. Navigate to `/admin/`
2. Login with superuser credentials
3. Click on "Validation Management" section

### Common Admin Tasks

#### Creating a Plan in Admin
1. Click "Validation Plans" → "Add Validation Plan"
2. Fill in Title, System Name, System Version
3. Write Description and Scope
4. Select Validation Approach
5. Select Responsible Person
6. Set Status (defaults to "draft")
7. Click "Save"

#### Bulk Updating Protocols
1. Go to "Validation Protocols" list
2. Check boxes for protocols to update
3. Select action from dropdown (e.g., "Change status to approved")
4. Click "Go"

#### Searching for Test Cases
1. Go to "Validation Test Cases" list
2. Use search box for title/description
3. Filter by Type, Status, Priority
4. Filter by Execution Date range

---

## Django Management Commands (Optional)

Create custom management commands in `validation_mgmt/management/commands/`:

```python
# validation_mgmt/management/commands/generate_test_data.py
from django.core.management.base import BaseCommand
from validation_mgmt.models import ValidationPlan
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Generate sample validation data'

    def handle(self, *args, **options):
        user = User.objects.first()
        plan = ValidationPlan.objects.create(
            title='Sample Validation Plan',
            system_name='Sample System',
            system_version='1.0',
            description='This is a sample',
            scope='Complete system',
            validation_approach='traditional_csv',
            responsible_person=user,
        )
        self.stdout.write(f'Created plan: {plan.plan_id}')
```

Usage: `python manage.py generate_test_data`

---

## Testing with Django Test Framework

```python
# validation_mgmt/tests.py
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from validation_mgmt.models import ValidationPlan

class ValidationPlanAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@test.com', 'pass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_validation_plan(self):
        data = {
            'title': 'Test Plan',
            'system_name': 'Test System',
            'system_version': '1.0',
            'description': 'Test description',
            'scope': 'Test scope',
            'validation_approach': 'traditional_csv',
            'responsible_person': self.user.id,
        }
        response = self.client.post('/api/validation/validation-plans/', data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['plan_id'], 'VP-0001')

    def test_list_plans_filtered(self):
        ValidationPlan.objects.create(
            title='Plan 1', system_name='System 1', system_version='1.0',
            description='Test', scope='Test', responsible_person=self.user, status='draft'
        )
        response = self.client.get('/api/validation/validation-plans/?status=draft')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_approve_plan(self):
        plan = ValidationPlan.objects.create(
            title='Plan', system_name='System', system_version='1.0',
            description='Test', scope='Test', responsible_person=self.user
        )
        response = self.client.post(f'/api/validation/validation-plans/{plan.id}/approve/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'approved')
```

Run tests: `python manage.py test validation_mgmt`

---

## Performance Tips

1. **Use select_related() for Foreign Keys:**
   ```python
   plans = ValidationPlan.objects.select_related(
       'responsible_person', 'qa_reviewer', 'department'
   )
   ```

2. **Use prefetch_related() for Reverse Relations:**
   ```python
   plans = ValidationPlan.objects.prefetch_related('protocols', 'rtm_entries')
   ```

3. **Index frequently searched fields:**
   ```python
   class ValidationPlan(AuditedModel):
       class Meta:
           indexes = [
               models.Index(fields=['status', '-created_at']),
           ]
   ```

4. **Use pagination for large datasets** (default 20/page)

5. **Cache summary endpoints:**
   ```python
   from django.views.decorators.cache import cache_page

   @cache_page(60 * 5)  # 5 minutes
   @action(detail=True, methods=['get'])
   def summary(self, request, pk=None):
       ...
   ```

---

## Monitoring & Logging

Enable logging in `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'validation_mgmt.log',
        },
    },
    'loggers': {
        'validation_mgmt': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

Then in views:
```python
import logging
logger = logging.getLogger('validation_mgmt')
logger.info(f'Plan {plan.plan_id} approved by {request.user}')
```
