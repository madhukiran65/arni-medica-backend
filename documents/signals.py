import hashlib
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from documents.models import Document, DocumentVersion


@receiver(pre_save, sender=Document)
def calculate_document_file_hash(sender, instance, **kwargs):
    """Calculate SHA-256 hash of the uploaded file."""
    if instance.file:
        if instance.file.size > 0:
            # Read file content and calculate hash
            instance.file.seek(0)
            file_hash = hashlib.sha256(instance.file.read()).hexdigest()
            instance.file_hash = file_hash
            instance.file.seek(0)


@receiver(pre_save, sender=DocumentVersion)
def calculate_version_file_hash(sender, instance, **kwargs):
    """Calculate SHA-256 hash of the version file."""
    if instance.file:
        if instance.file.size > 0:
            # Read file content and calculate hash
            instance.file.seek(0)
            file_hash = hashlib.sha256(instance.file.read()).hexdigest()
            instance.file_hash = file_hash
            instance.file.seek(0)


@receiver(post_save, sender=Document)
def create_initial_document_version(sender, instance, created, **kwargs):
    """Create initial document version when document is created."""
    if created:
        DocumentVersion.objects.create(
            document=instance,
            version_number=instance.version,
            created_by=instance.owner,
            file=instance.file,
            file_hash=instance.file_hash,
            change_summary='Initial version'
        )
