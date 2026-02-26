"""
Safety migration: ensures department.code, department.head, department.parent,
department.is_active, and all new user model fields exist in the database.
This handles the case where migration 0002 was recorded as applied but
the unique constraint on 'code' prevented the column from being created.
"""
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def forwards(apps, schema_editor):
    """Check and fix any missing columns."""
    from django.db import connection
    cursor = connection.cursor()

    # Check if department.code column exists
    cursor.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'users_department' AND column_name = 'code'
    """)
    if not cursor.fetchone():
        cursor.execute('ALTER TABLE users_department ADD COLUMN code varchar(20) DEFAULT %s', [''])

    cursor.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'users_department' AND column_name = 'is_active'
    """)
    if not cursor.fetchone():
        cursor.execute('ALTER TABLE users_department ADD COLUMN is_active boolean DEFAULT true')

    cursor.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'users_department' AND column_name = 'head_id'
    """)
    if not cursor.fetchone():
        cursor.execute('ALTER TABLE users_department ADD COLUMN head_id integer NULL')

    cursor.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'users_department' AND column_name = 'parent_id'
    """)
    if not cursor.fetchone():
        cursor.execute('ALTER TABLE users_department ADD COLUMN parent_id integer NULL')

    # Check UserProfile new fields
    for col, col_type, default in [
        ('title', 'varchar(100)', "''"),
        ('phone', 'varchar(30)', "''"),
        ('site_id', 'integer', 'NULL'),
        ('job_function_id', 'integer', 'NULL'),
        ('supervisor_id', 'integer', 'NULL'),
    ]:
        cursor.execute(f"""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'users_userprofile' AND column_name = '{col}'
        """)
        if not cursor.fetchone():
            null_clause = 'NULL' if default == 'NULL' else f'DEFAULT {default}'
            cursor.execute(f'ALTER TABLE users_userprofile ADD COLUMN {col} {col_type} {null_clause}')

    cursor.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'users_userprofile' AND column_name = 'date_of_joining'
    """)
    if not cursor.fetchone():
        cursor.execute('ALTER TABLE users_userprofile ADD COLUMN date_of_joining date NULL')

    # Check Role new fields
    role_fields = [
        'can_release_documents', 'can_obsolete_documents', 'can_approve_capa',
        'can_investigate_complaints', 'can_create_deviations', 'can_approve_deviations',
        'can_create_change_controls', 'can_approve_change_controls', 'can_assign_training',
        'can_create_courses', 'can_lead_audit', 'can_manage_suppliers', 'can_qualify_suppliers',
        'can_create_forms', 'can_publish_forms', 'can_manage_settings', 'can_manage_workflows',
        'can_export_data', 'is_active',
    ]
    for field in role_fields:
        cursor.execute(f"""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'users_role' AND column_name = '{field}'
        """)
        if not cursor.fetchone():
            cursor.execute(f'ALTER TABLE users_role ADD COLUMN {field} boolean DEFAULT false')

    # Create Site table if not exists
    cursor.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_name = 'users_site'
    """)
    if not cursor.fetchone():
        cursor.execute("""
            CREATE TABLE users_site (
                id BIGSERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                code VARCHAR(20) DEFAULT '',
                address TEXT DEFAULT '',
                city VARCHAR(100) DEFAULT '',
                state VARCHAR(100) DEFAULT '',
                country VARCHAR(100) DEFAULT '',
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            )
        """)

    # Create ProductLine table if not exists
    cursor.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_name = 'users_productline'
    """)
    if not cursor.fetchone():
        cursor.execute("""
            CREATE TABLE users_productline (
                id BIGSERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                code VARCHAR(20) DEFAULT '',
                description TEXT DEFAULT '',
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            )
        """)

    # Remove unique constraint on code if it exists
    try:
        cursor.execute("""
            SELECT constraint_name FROM information_schema.table_constraints
            WHERE table_name = 'users_department' AND constraint_type = 'UNIQUE'
            AND constraint_name LIKE '%code%'
        """)
        for row in cursor.fetchall():
            cursor.execute(f'ALTER TABLE users_department DROP CONSTRAINT {row[0]}')
    except Exception:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_productline_site_department_code_department_head_and_more'),
        ('training', '0002_trainingassessment_assessment_type_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
