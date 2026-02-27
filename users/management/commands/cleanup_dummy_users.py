"""
Management command to remove dummy/seed users.
Keeps only specified users (by username) and deletes the rest.
Reassigns all related records to admin before deleting.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import connection

User = get_user_model()

KEEP_USERNAMES = ['admin', 'rakesh.admin']


class Command(BaseCommand):
    help = 'Delete all dummy users except Admin User and Rakesh Garimella'

    def handle(self, *args, **options):
        admin_user = User.objects.get(username='admin')
        keep_users = User.objects.filter(username__in=KEEP_USERNAMES)
        keep_ids = set(keep_users.values_list('id', flat=True))

        to_delete = User.objects.exclude(id__in=keep_ids)
        delete_ids = list(to_delete.values_list('id', flat=True))
        count = len(delete_ids)

        if count == 0:
            self.stdout.write(self.style.SUCCESS("No dummy users to delete."))
            return

        self.stdout.write(f"Reassigning records from {count} users to admin (id={admin_user.id})...")

        cursor = connection.cursor()

        # Find all FK columns pointing to auth_user
        cursor.execute("""
            SELECT tc.table_name, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
                ON tc.constraint_name = ccu.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND ccu.table_name = 'auth_user'
              AND ccu.column_name = 'id'
        """)
        fk_refs = cursor.fetchall()

        for table, column in fk_refs:
            # Skip the user profile table - we'll delete those
            if table == 'users_userprofile':
                continue

            # Check if column is nullable
            cursor.execute(f"""
                SELECT is_nullable FROM information_schema.columns
                WHERE table_name = %s AND column_name = %s
            """, [table, column])
            row = cursor.fetchone()
            is_nullable = row and row[0] == 'YES'

            placeholders = ','.join(['%s'] * len(delete_ids))

            if is_nullable:
                # Set nullable FKs to NULL
                cursor.execute(
                    f"UPDATE {table} SET {column} = NULL WHERE {column} IN ({placeholders})",
                    delete_ids
                )
            else:
                # Reassign non-nullable FKs to admin
                cursor.execute(
                    f"UPDATE {table} SET {column} = %s WHERE {column} IN ({placeholders})",
                    [admin_user.id] + delete_ids
                )
            affected = cursor.rowcount
            if affected > 0:
                action = 'nulled' if is_nullable else 'reassigned'
                self.stdout.write(f"  {table}.{column}: {action} {affected} rows")

        # Delete user profiles first
        placeholders = ','.join(['%s'] * len(delete_ids))
        cursor.execute(
            f"DELETE FROM users_userprofile WHERE user_id IN ({placeholders})",
            delete_ids
        )
        self.stdout.write(f"  Deleted {cursor.rowcount} user profiles")

        # Now delete the users
        cursor.execute(
            f"DELETE FROM auth_user WHERE id IN ({placeholders})",
            delete_ids
        )
        self.stdout.write(self.style.SUCCESS(
            f"Successfully deleted {cursor.rowcount} dummy users. "
            f"Kept: {list(KEEP_USERNAMES)}"
        ))
