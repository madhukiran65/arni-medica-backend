from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from equipment.models import (
    Equipment,
    CalibrationSchedule,
    MaintenanceSchedule,
    CalibrationRecord,
    MaintenanceRecord,
)


@receiver(post_save, sender=Equipment)
def create_default_schedules(sender, instance, created, **kwargs):
    if created:
        if instance.requires_calibration and not hasattr(instance, 'calibration_schedule'):
            CalibrationSchedule.objects.create(
                equipment=instance,
                interval_days=365,
                auto_quarantine_on_overdue=True,
                reminder_days_before=30,
            )

        if instance.requires_maintenance:
            MaintenanceSchedule.objects.create(
                equipment=instance,
                maintenance_type='preventive',
                interval_days=180,
                description=f'Preventive maintenance for {instance.name}',
            )


@receiver(post_save, sender=CalibrationRecord)
def update_calibration_schedule(sender, instance, created, **kwargs):
    if created:
        try:
            schedule = CalibrationSchedule.objects.get(equipment=instance.equipment)
            if instance.result in ['pass', 'adjusted_pass']:
                schedule.last_calibrated = instance.calibration_date
                schedule.next_due = instance.calibration_date + timedelta(days=schedule.interval_days)
                schedule.save()

                equipment = instance.equipment
                if equipment.status == 'quarantined' and instance.result != 'out_of_tolerance':
                    equipment.status = 'active'
                    equipment.save()
        except CalibrationSchedule.DoesNotExist:
            pass


@receiver(post_save, sender=MaintenanceRecord)
def update_maintenance_schedule(sender, instance, created, **kwargs):
    if created and instance.status == 'completed':
        try:
            schedule = MaintenanceSchedule.objects.get(
                equipment=instance.equipment,
                maintenance_type=instance.maintenance_type
            )
            schedule.last_performed = instance.maintenance_date
            schedule.next_due = instance.maintenance_date + timedelta(days=schedule.interval_days)
            schedule.save()
        except MaintenanceSchedule.DoesNotExist:
            pass


@receiver(post_save, sender=CalibrationSchedule)
def check_calibration_overdue(sender, instance, **kwargs):
    if instance.auto_quarantine_on_overdue and instance.next_due:
        if timezone.now().date() > instance.next_due:
            equipment = instance.equipment
            if equipment.status == 'active':
                equipment.status = 'quarantined'
                equipment.save()
