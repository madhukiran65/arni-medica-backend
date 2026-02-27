"""
Management command to remove dummy/seed users.
Keeps only specified users (by username) and deletes the rest.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

# Usernames to KEEP — everything else gets deleted
KEEP_USERNAMES = ['admin', 'rakesh.admin']


class Command(BaseCommand):
    help = 'Delete all dummy users except Admin User and Rakesh Garimella'

    def handle(self, *args, **options):
        keep_users = User.objects.filter(username__in=KEEP_USERNAMES)
        keep_ids = list(keep_users.values_list('id', flat=True))
        keep_names = list(keep_users.values_list('username', flat=True))

        self.stdout.write(f"Keeping users: {keep_names} (IDs: {keep_ids})")

        to_delete = User.objects.exclude(id__in=keep_ids)
        count = to_delete.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS("No dummy users to delete."))
            return

        self.stdout.write(f"Deleting {count} dummy users...")
        deleted_names = list(to_delete.values_list('username', flat=True))
        to_delete.delete()
        self.stdout.write(self.style.SUCCESS(
            f"Successfully deleted {count} users: {deleted_names}"
        ))
