# Design Controls App - Implementation Checklist

## Pre-Installation

- [ ] Ensure Django 3.2+ is installed
- [ ] Ensure Django REST Framework 3.12+ is installed
- [ ] Ensure django-filter 2.4+ is installed
- [ ] Ensure core.models.AuditedModel exists in your project
- [ ] Ensure users.models has Department, ProductLine, Site models
- [ ] Review INTEGRATION.md for dependency requirements

## Installation Steps

### Step 1: Add to INSTALLED_APPS
- [ ] Open your Django settings file (settings.py or settings/base.py)
- [ ] Add 'design_controls' to INSTALLED_APPS list
- [ ] Verify REST_FRAMEWORK configuration exists

### Step 2: Configure URLs
- [ ] Open your main urls.py
- [ ] Add: `path('api/design-controls/', include('design_controls.urls'))`
- [ ] Verify import: `from django.urls import path, include`

### Step 3: Run Migrations
```bash
python manage.py makemigrations design_controls
python manage.py migrate design_controls
```
- [ ] Confirm migrations created successfully
- [ ] Confirm migrations applied to database

### Step 4: Verify Installation
```bash
python manage.py shell
>>> from design_controls.models import DesignProject
>>> DesignProject.objects.all()
<QuerySet []>
```
- [ ] No errors on import
- [ ] Can query models

### Step 5: Access Admin Interface
- [ ] Start development server: `python manage.py runserver`
- [ ] Navigate to http://localhost:8000/admin/
- [ ] Log in with superuser account
- [ ] Verify Design Controls section appears
- [ ] Verify all 8 models are listed:
  - [ ] Design Projects
  - [ ] User Needs
  - [ ] Design Inputs
  - [ ] Design Outputs
  - [ ] VV Protocols
  - [ ] Design Reviews
  - [ ] Design Transfers
  - [ ] Traceability Links

### Step 6: Test API Endpoints
- [ ] Test GET /api/design-controls/design-projects/
- [ ] Test creating a DesignProject via API
- [ ] Verify auto-ID generation (DP-0001)
- [ ] Test filtering: ?status=active
- [ ] Test search: ?search=DP-0001

## Configuration (Optional but Recommended)

### File Upload Support
- [ ] Configure MEDIA_URL in settings.py
- [ ] Configure MEDIA_ROOT in settings.py
- [ ] Add media URL routing in main urls.py

### API Documentation
- [ ] Install drf-spectacular: `pip install drf-spectacular`
- [ ] Add to INSTALLED_APPS: 'drf_spectacular'
- [ ] Configure schema and Swagger URLs
- [ ] Test at /api/docs/

### Authentication
- [ ] Configure DEFAULT_AUTHENTICATION_CLASSES in REST_FRAMEWORK
- [ ] Configure DEFAULT_PERMISSION_CLASSES in REST_FRAMEWORK
- [ ] Create test tokens for API testing
- [ ] Test authenticated requests

### Logging
- [ ] Configure LOGGING in settings.py
- [ ] Create logs directory
- [ ] Verify logs are being written

## Database Verification

### Django ORM
- [ ] Create test DesignProject: `DesignProject.objects.create(...)`
- [ ] Verify auto-ID generated correctly (DP-0001)
- [ ] Create related objects (UserNeed, DesignInput, etc.)
- [ ] Verify M2M relationships work
- [ ] Test filtering and search

### Database Checks
- [ ] Run: `python manage.py check`
- [ ] Verify all database migrations applied
- [ ] Check database constraints are in place

## Admin Interface Testing

### Create Objects
- [ ] Create a DesignProject in admin
- [ ] Create UserNeeds linked to the project
- [ ] Create DesignInputs
- [ ] Create DesignOutputs
- [ ] Create VVProtocols
- [ ] Create DesignReviews
- [ ] Create DesignTransfers
- [ ] Create TraceabilityLinks

### Test Filtering
- [ ] Filter by status
- [ ] Filter by priority
- [ ] Filter by phase
- [ ] Combine multiple filters
- [ ] Test date range filters

### Test Search
- [ ] Search by project_id
- [ ] Search by title
- [ ] Search by description

### Test M2M Management
- [ ] Add user needs to design inputs
- [ ] Add design inputs to design outputs
- [ ] Add attendees to design reviews
- [ ] Verify links are saved correctly

## API Testing

### Create via API
- [ ] POST to /api/design-controls/design-projects/
- [ ] Verify response includes auto-generated ID
- [ ] POST to other endpoints
- [ ] Verify all required fields validate

### Read via API
- [ ] GET /api/design-controls/design-projects/
- [ ] Verify pagination works
- [ ] Verify search parameter works
- [ ] GET specific object by ID
- [ ] Verify nested relationships display

### Update via API
- [ ] PATCH to update status field
- [ ] PATCH to update approval fields
- [ ] PUT to replace entire object
- [ ] Verify updated_at timestamp changes

### Delete via API
- [ ] DELETE to remove object
- [ ] Verify 204 response
- [ ] Verify object no longer exists

### Custom Actions
- [ ] GET /api/design-controls/design-projects/{id}/traceability_report/
- [ ] POST /api/design-controls/vv-protocols/{id}/mark_executed/
- [ ] Verify responses are correct

## Filter Testing

### Choice Filters
- [ ] ?status=active
- [ ] ?current_phase=design_input
- [ ] ?product_type=device
- [ ] ?priority=critical

### FK Filters
- [ ] ?project=1
- [ ] ?approved_by=1
- [ ] ?executed_by=1

### Date Range Filters
- [ ] ?target_completion_date_from=2024-01-01
- [ ] ?target_completion_date_to=2024-12-31
- [ ] ?execution_date_from=2024-03-01

### Boolean Filters
- [ ] ?production_readiness_confirmed=true
- [ ] ?production_readiness_confirmed=false

### Combined Filters
- [ ] ?status=approved&priority=critical&project=1
- [ ] Multiple filters on one query

## Workflow Testing (Complete Scenario)

- [ ] Create DesignProject (gets DP-0001)
- [ ] Create 3 UserNeeds (UN-0001, UN-0002, UN-0003)
- [ ] Create 3 DesignInputs linked to UserNeeds
- [ ] Create 2 DesignOutputs linked to DesignInputs
- [ ] Create VVProtocols linked to Inputs/Outputs
- [ ] Execute VVProtocol (result=pass)
- [ ] Conduct DesignReview (outcome=approved)
- [ ] Create TraceabilityLinks
- [ ] Get traceability_report (should show no missing links)
- [ ] Create DesignTransfer
- [ ] Update status through phases
- [ ] Query all models with filters and search

## Documentation Verification

- [ ] README.md covers all models and endpoints
- [ ] EXAMPLES.md shows complete workflow
- [ ] INTEGRATION.md has setup instructions
- [ ] All code examples work correctly
- [ ] Troubleshooting section addresses common issues

## Performance Testing

- [ ] Create 100+ objects in database
- [ ] Test list endpoint response time (should be <1s)
- [ ] Test search with large dataset
- [ ] Test filter with large dataset
- [ ] Verify indexes are being used

## Security Testing

- [ ] Test without authentication (should fail if required)
- [ ] Test with invalid token
- [ ] Test with valid token
- [ ] Verify read-only fields can't be written
- [ ] Verify sensitive fields are protected

## Edge Cases

- [ ] Create object with minimal required fields
- [ ] Create object with all optional fields
- [ ] Test duplicate IDs (should fail gracefully)
- [ ] Test invalid choice values
- [ ] Test null/blank fields according to spec
- [ ] Test concurrent object creation

## Data Integrity

- [ ] Verify cascade deletes work correctly
- [ ] Verify M2M relationships persist
- [ ] Verify audit fields are populated
- [ ] Verify timestamps are accurate
- [ ] Verify created_by/updated_by track users

## File Upload Testing

- [ ] Upload PDF to DesignOutput.file
- [ ] Upload to VVProtocol.file
- [ ] Upload to VVProtocol.result_file
- [ ] Verify files are stored correctly
- [ ] Verify file URLs are accessible

## Audit Trail Testing

- [ ] Verify created_at is set on creation
- [ ] Verify updated_at changes on update
- [ ] Verify created_by is set to current user
- [ ] Verify updated_by changes on update
- [ ] Verify audit fields are read-only in API

## Admin Customization Verification

- [ ] All list_displays show expected fields
- [ ] All list_filters work correctly
- [ ] All search_fields return correct results
- [ ] All fieldsets organize fields logically
- [ ] Read-only fields can't be edited
- [ ] M2M fields show proper widgets

## Production Checklist

- [ ] DEBUG = False in production settings
- [ ] ALLOWED_HOSTS configured correctly
- [ ] CSRF protection enabled
- [ ] HTTPS enabled
- [ ] Database backed up regularly
- [ ] Log files monitored
- [ ] Performance monitoring active
- [ ] Error tracking configured (Sentry, etc.)
- [ ] API rate limiting configured (if needed)
- [ ] Database indexes created
- [ ] Static files collected

## Final Verification

- [ ] All 12 files exist in correct directory
- [ ] All Python files are syntactically correct
- [ ] All imports resolve without errors
- [ ] All database migrations are applied
- [ ] All admin pages load without error
- [ ] All API endpoints respond correctly
- [ ] All filters work as expected
- [ ] All custom actions function properly
- [ ] All documentation is accurate and complete

## Sign-Off

- [ ] Installation Date: ________________
- [ ] Verified By: ________________
- [ ] Production Ready: [ ] Yes [ ] No

## Post-Deployment

- [ ] Monitor application logs for errors
- [ ] Verify API response times
- [ ] Check database performance
- [ ] Monitor disk space usage
- [ ] Verify backups are running
- [ ] Test restore procedures
- [ ] Monitor user adoption
- [ ] Collect feedback for improvements

---

**Notes:**
Use this checklist to ensure complete and proper installation of the Design Controls app.
Address any failed checks before considering the app ready for production use.
Keep this checklist for compliance and audit purposes.
