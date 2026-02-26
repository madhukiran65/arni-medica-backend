"""
Complete schema upgrade for users app — idempotent RunPython migration.
Uses raw SQL with existence checks so it works on both fresh and partial DBs.
Only depends on users.0001_initial (no cross-app dependencies).
"""
from django.db import migrations


def forwards(apps, schema_editor):
    from django.db import connection
    cursor = connection.cursor()

    def col_exists(table, column):
        cursor.execute(
            "SELECT 1 FROM information_schema.columns WHERE table_name=%s AND column_name=%s",
            [table, column]
        )
        return cursor.fetchone() is not None

    def tbl_exists(table):
        cursor.execute(
            "SELECT 1 FROM information_schema.tables WHERE table_name=%s",
            [table]
        )
        return cursor.fetchone() is not None

    # ── Department new columns ──
    for col, ddl in [
        ('code',      "varchar(20) NOT NULL DEFAULT ''"),
        ('is_active', "boolean NOT NULL DEFAULT true"),
        ('head_id',   "integer NULL"),
        ('parent_id', "integer NULL"),
    ]:
        if not col_exists('users_department', col):
            cursor.execute(f"ALTER TABLE users_department ADD COLUMN {col} {ddl}")

    # Remove accidental unique constraint on code
    try:
        cursor.execute("""
            SELECT constraint_name FROM information_schema.table_constraints
            WHERE table_name='users_department' AND constraint_type='UNIQUE'
              AND constraint_name LIKE '%%code%%'
        """)
        for row in cursor.fetchall():
            cursor.execute(f"ALTER TABLE users_department DROP CONSTRAINT IF EXISTS {row[0]}")
    except Exception:
        pass

    # ── Site table ──
    if not tbl_exists('users_site'):
        cursor.execute("""
            CREATE TABLE users_site (
                id BIGSERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                code VARCHAR(20) NOT NULL DEFAULT '',
                address TEXT NOT NULL DEFAULT '',
                city VARCHAR(100) NOT NULL DEFAULT '',
                state VARCHAR(100) NOT NULL DEFAULT '',
                country VARCHAR(100) NOT NULL DEFAULT '',
                is_active BOOLEAN NOT NULL DEFAULT true,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            )
        """)

    # ── ProductLine table ──
    if not tbl_exists('users_productline'):
        cursor.execute("""
            CREATE TABLE users_productline (
                id BIGSERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                code VARCHAR(20) NOT NULL DEFAULT '',
                description TEXT NOT NULL DEFAULT '',
                is_active BOOLEAN NOT NULL DEFAULT true,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            )
        """)

    # ── Role new permission columns ──
    for f in [
        'can_release_documents', 'can_obsolete_documents', 'can_approve_capa',
        'can_investigate_complaints', 'can_create_deviations', 'can_approve_deviations',
        'can_create_change_controls', 'can_approve_change_controls',
        'can_assign_training', 'can_create_courses', 'can_lead_audit',
        'can_manage_suppliers', 'can_qualify_suppliers',
        'can_create_forms', 'can_publish_forms',
        'can_manage_settings', 'can_manage_workflows', 'can_export_data',
        'is_active',
    ]:
        if not col_exists('users_role', f):
            cursor.execute(f"ALTER TABLE users_role ADD COLUMN {f} boolean NOT NULL DEFAULT false")

    # ── UserProfile new columns ──
    for col, ddl in [
        ('title',           "varchar(100) NOT NULL DEFAULT ''"),
        ('phone',           "varchar(30) NOT NULL DEFAULT ''"),
        ('date_of_joining', "date NULL"),
        ('site_id',         "bigint NULL"),
        ('job_function_id', "bigint NULL"),
        ('supervisor_id',   "integer NULL"),
    ]:
        if not col_exists('users_userprofile', col):
            cursor.execute(f"ALTER TABLE users_userprofile ADD COLUMN {col} {ddl}")

    # ── M2M: UserProfile ↔ ProductLine ──
    if not tbl_exists('users_userprofile_product_lines'):
        cursor.execute("""
            CREATE TABLE users_userprofile_product_lines (
                id BIGSERIAL PRIMARY KEY,
                userprofile_id bigint NOT NULL REFERENCES users_userprofile(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
                productline_id bigint NOT NULL REFERENCES users_productline(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
                UNIQUE (userprofile_id, productline_id)
            )
        """)

    # ── Fake-record migration 0003 since we already applied the schema ──
    cursor.execute(
        "SELECT 1 FROM django_migrations WHERE app='users' AND name=%s",
        ['0003_productline_site_department_code_department_head_and_more']
    )
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES ('users', %s, NOW())",
            ['0003_productline_site_department_code_department_head_and_more']
        )


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
