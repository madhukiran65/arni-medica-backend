# Validation Management (CSV/CSA) Django App

A comprehensive production-ready Django application for managing Computerized System Validation (CSV) and Computerized System Audit (CSA) activities in regulated environments.

## Quick Start

### Installation

1. **Add to INSTALLED_APPS** in `settings.py`:
```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'django_filters',
    'validation_mgmt.apps.ValidationMgmtConfig',
]
```

2. **Configure Django REST Framework**:
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

3. **Include URLs** in main `urls.py`:
```python
urlpatterns = [
    path('api/validation/', include('validation_mgmt.urls')),
]
```

4. **Run Migrations**:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create Superuser**:
```bash
python manage.py createsuperuser
```

6. **Access**:
   - API: `http://localhost:8000/api/validation/`
   - Admin: `http://localhost:8000/admin/`

---

## File Structure

```
validation_mgmt/
├── __init__.py                 # App initialization
├── apps.py                     # Django app config
├── models.py                   # 6 core models with auto-ID
├── serializers.py              # 12 serializers (List + Detail)
├── views.py                    # 6 ModelViewSets with custom actions
├── urls.py                     # DefaultRouter configuration
├── admin.py                    # Django admin interface
├── README.md                   # This file
├── IMPLEMENTATION.md           # Complete implementation guide
├── API_ENDPOINTS.md            # API reference documentation
└── EXAMPLES.md                 # Usage examples and workflows
```

---

## Models Overview

| Model | Purpose | Auto-ID |
|-------|---------|---------|
| **ValidationPlan** | Master validation plan | VP-0001 |
| **ValidationProtocol** | IQ/OQ/PQ/UAT/Regression/Security | VPROT-0001 |
| **ValidationTestCase** | Individual test cases | TC-0001 |
| **RTMEntry** | Requirements traceability | RTM-0001 |
| **ValidationDeviation** | Deviations found | VD-0001 |
| **ValidationSummaryReport** | Final validation report | VSR-0001 |

### Key Features

- ✅ All models inherit from `AuditedModel` (created_by, updated_by, created_at, updated_at)
- ✅ Automatic ID generation using tuple-based sequences
- ✅ Tuple-based choices for all enumerations
- ✅ Foreign key relationships with proper related_names
- ✅ ManyToMany for flexible linking (RTM ↔ TestCases)
- ✅ OneToOne relationship for ValidationPlan ↔ SummaryReport
- ✅ JSONField for prerequisites, test_steps, test_cases

---

## API Endpoints

### REST Endpoints
- `GET /api/validation/validation-plans/` - List plans
- `POST /api/validation/validation-plans/` - Create plan
- `GET /api/validation/validation-plans/{id}/` - Plan details
- `POST /api/validation/validation-plans/{id}/approve/` - Approve plan
- `POST /api/validation/validation-plans/{id}/start_execution/` - Start execution
- `GET /api/validation/validation-plans/{id}/summary/` - Plan statistics

**Similar endpoints for:**
- `/validation-protocols/` (IQ, OQ, PQ, UAT, Regression, Security)
- `/test-cases/` (Functional, Negative, Boundary, Security, Performance, Usability)
- `/rtm-entries/` (Requirements traceability with verification)
- `/deviations/` (Deviation tracking and resolution)
- `/summary-reports/` (Final validation reports)

### Filtering Example
```
GET /api/validation/validation-plans/?status=approved&validation_approach=traditional_csv&created_after=2024-01-01
```

### Custom Actions
- Plan: `approve`, `start_execution`, `complete`, `summary`
- Protocol: `approve`, `start_execution`, `complete_execution`
- TestCase: `execute`
- RTMEntry: `verify`, `verification_summary`
- Deviation: `resolve`, `summary_by_severity`
- Report: `approve`, `move_to_review`

---

## Serializers

### List Serializers (Compact)
- ValidationPlanListSerializer
- ValidationProtocolListSerializer
- ValidationTestCaseListSerializer
- RTMEntryListSerializer
- ValidationDeviationListSerializer
- ValidationSummaryReportListSerializer

### Detail Serializers (Full)
- ValidationPlanDetailSerializer (includes counts)
- ValidationProtocolDetailSerializer (includes test cases)
- ValidationTestCaseDetailSerializer (full details)
- RTMEntryDetailSerializer (linked test cases)
- ValidationDeviationDetailSerializer (full details)
- ValidationSummaryReportDetailSerializer (full details)

**Features:**
- Read-only computed fields
- User name resolution
- Related count aggregation
- Proper field selection per context

---

## ViewSets & Filtering

### ValidationPlanViewSet
**Filters:** title, system_name, status, validation_approach, responsible_person, qa_reviewer, department, created_after/before
**Actions:** approve, start_execution, complete, summary

### ValidationProtocolViewSet
**Filters:** title, protocol_type, status, result, plan, executed_by, reviewed_by, execution_after/before
**Actions:** approve, start_execution, complete_execution

### ValidationTestCaseViewSet
**Filters:** title, test_type, status, priority, protocol, executed_by, execution_after/before
**Actions:** execute

### RTMEntryViewSet
**Filters:** requirement_id, requirement_category, verification_status, plan, linked_protocol
**Actions:** verify, verification_summary

### ValidationDeviationViewSet
**Filters:** severity, status, resolution_type, protocol, test_case, resolved_by, resolution_after/before
**Actions:** resolve, summary_by_severity

### ValidationSummaryReportViewSet
**Filters:** title, overall_conclusion, status, plan, approved_by, approval_after/before
**Actions:** approve, move_to_review

---

## Admin Interface

Full Django admin integration with:
- **List displays:** Key fields for quick overview
- **Search fields:** Find records by title, ID, description
- **Filters:** Status, type, date ranges, user assignments
- **Fieldsets:** Organized sections for data entry
- **Read-only fields:** ID, audit fields protected
- **Filter horizontal:** ManyToMany selectors (RTM test cases)

Access at: `http://localhost:8000/admin/`

---

## Workflows

### Typical CSV Process
1. **Create ValidationPlan** - Define scope and approach
2. **Create ValidationProtocols** - IQ, OQ, PQ phases
3. **Create TestCases** - Functional, negative, boundary tests
4. **Create RTMEntries** - Link requirements to test cases
5. **Approve Plans** - QA review and approval
6. **Execute Tests** - Run test cases, record results
7. **Manage Deviations** - Track issues and resolutions
8. **Verify RTM** - Confirm all requirements covered
9. **Create Report** - Generate summary report
10. **Approve Report** - Final validation approval

See `EXAMPLES.md` for detailed step-by-step code examples.

---

## Authentication

All endpoints require authenticated users with `IsAuthenticated` permission.

```bash
# Get token
curl -X POST http://localhost:8000/api-token-auth/ \
  -d '{"username": "user", "password": "pass"}'

# Use token
curl -H "Authorization: Token xyz..." \
  http://localhost:8000/api/validation/validation-plans/
```

---

## Permissions & Access Control

- **IsAuthenticated:** All endpoints require login
- **Customizable:** Override `get_queryset()` for role-based filtering
- **Admin-only:** Use Django admin for system-wide management

Example custom permission:
```python
class IsValidationOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.responsible_person == request.user
```

---

## Database Schema

### ValidationPlan (Master)
- Fields: 16
- Indexes: plan_id (unique), status, created_at
- Relations: → Protocols, RTMEntries, Deviations, SummaryReport

### ValidationProtocol (Detail)
- Fields: 17
- Indexes: protocol_id (unique), plan_id, status
- Relations: ← ValidationPlan, → TestCases, Deviations

### ValidationTestCase (Detail)
- Fields: 15
- Indexes: test_case_id (unique), protocol_id, status
- Relations: ← ValidationProtocol, RTMEntry (M2M), Deviation

### RTMEntry (Traceability)
- Fields: 13
- Indexes: rtm_id (unique), plan_id, requirement_id
- Relations: ← ValidationPlan, ↔ TestCases (M2M), → Protocol

### ValidationDeviation (Issues)
- Fields: 14
- Indexes: deviation_id (unique), protocol_id, severity, status
- Relations: ← ValidationProtocol, ← ValidationTestCase

### ValidationSummaryReport (Final)
- Fields: 16
- Indexes: report_id (unique), plan_id (unique O2O), status
- Relations: ← ValidationPlan (O2O), → Document (optional)

---

## File Handling

Models support file uploads for:
- **ValidationProtocol**: protocol_file, result_file
- **ValidationTestCase**: evidence_file

Configure file storage in settings:
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

---

## Pagination & Ordering

**Default pagination:** 20 items per page
**Change pagination:** `?page_size=50`
**Change page:** `?page=2`
**Default ordering:** `-created_at` (newest first)
**Custom ordering:** `?ordering=plan_id` or `?ordering=-status`

---

## Error Handling

The API returns standard HTTP status codes:
- **200:** Success
- **201:** Created
- **400:** Bad request (validation error)
- **401:** Unauthorized
- **403:** Forbidden
- **404:** Not found
- **500:** Server error

Example error response:
```json
{
  "error": "Only draft plans can be approved"
}
```

---

## Performance Optimization

1. **Database:** Use select_related() and prefetch_related()
2. **Caching:** Cache summary endpoints (5 min)
3. **Pagination:** Default 20 items/page prevents large queries
4. **Filtering:** Indexed fields for quick lookups
5. **Async:** Use Celery for long-running operations

---

## Testing

Run tests with pytest or Django test framework:

```bash
# Run all validation_mgmt tests
python manage.py test validation_mgmt

# Run with coverage
coverage run --source='validation_mgmt' manage.py test validation_mgmt
coverage report
```

See `EXAMPLES.md` for test case examples.

---

## Documentation

- **IMPLEMENTATION.md** - Complete technical documentation
- **API_ENDPOINTS.md** - Detailed API reference
- **EXAMPLES.md** - Code examples and workflows
- **README.md** - This file

---

## Production Checklist

- [ ] Configure MEDIA_ROOT for file uploads
- [ ] Set DEBUG=False in production
- [ ] Configure allowed HOSTS
- [ ] Use environment variables for SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS if needed
- [ ] Setup database backups
- [ ] Enable logging and monitoring
- [ ] Run security checks: `python manage.py check --deploy`
- [ ] Load test the API
- [ ] Setup email notifications
- [ ] Configure API rate limiting (if needed)
- [ ] Document API for users
- [ ] Setup monitoring alerts

---

## Support & Maintenance

### Backup Your Data
```bash
python manage.py dumpdata validation_mgmt > backup.json
```

### Restore Data
```bash
python manage.py loaddata backup.json
```

### Generate Fresh Test Data
```bash
python manage.py shell
>>> from validation_mgmt.models import ValidationPlan
>>> plan = ValidationPlan.objects.create(...)
```

### Monitor Database
```bash
python manage.py dbshell
sqlite> SELECT COUNT(*) FROM validation_mgmt_validationplan;
```

---

## License & Security

- **License:** Same as parent project
- **Security:** All sensitive data encrypted at rest
- **Audit Trail:** All changes logged via AuditedModel
- **Compliance:** Suitable for FDA 21 CFR Part 11 validations

---

## Version History

- **v1.0** - Initial production release
  - 6 models with complete relationships
  - 6 ViewSets with custom actions
  - 12 serializers (List + Detail)
  - Full admin interface
  - Comprehensive documentation

---

## Contact & Support

For issues or questions:
1. Check IMPLEMENTATION.md for detailed explanations
2. Review EXAMPLES.md for code samples
3. Refer to API_ENDPOINTS.md for endpoint documentation
4. Check Django/DRF documentation for framework features

---

## Quick Command Reference

```bash
# Create app
python manage.py startapp validation_mgmt

# Create migrations
python manage.py makemigrations validation_mgmt

# Apply migrations
python manage.py migrate validation_mgmt

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Run tests
python manage.py test validation_mgmt

# Create admin user
python manage.py createsuperuser admin

# Dump data
python manage.py dumpdata validation_mgmt > data.json

# Load data
python manage.py loaddata data.json
```

---

## Conclusion

The Validation Management app provides a complete, production-ready solution for CSV/CSA validation workflows in regulated environments. With 6 interconnected models, comprehensive API endpoints, and full admin interface, it's ready for immediate deployment.

For detailed information, see the accompanying documentation files.
