from django.db import models
from django.utils.translation import gettext_lazy as _
from django_cryptography.fields import encrypt
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid

class Doctor(models.Model):
    """
    Doctor model for the health appointment system
    """

    SPECIALITIES = [
        ('Mental', 'Mental'),
        ('General', 'General'),
        ('Density', 'Density'),
        ('Physiotherapy', 'Physiotherapy'),
        ('Chiropractic', 'Chiropractic'),
        ('Audiology', 'Audiology'),
        ('Optometry', 'Optometry'),
    ]

    doctor_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    speciality = models.CharField(max_length=50, choices=SPECIALITIES)
    dob = models.DateField()
    experience = models.IntegerField()
    working_day = models.CharField(max_length=20, help_text="Comma-separated list of working days (1-7)")
    from_time = models.TimeField()
    to_time = models.TimeField()
    description = models.TextField()
    
    # Working hours
    DAYS_OF_WEEK = [
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
        (7, 'Sunday'),
    ]
    working_days = models.CharField(max_length=20, help_text="Comma-separated list of working days (1-7)")
    work_start_time = models.TimeField(verbose_name="Working hours from")
    work_end_time = models.TimeField(verbose_name="Working hours to")
    is_available = models.BooleanField(default=True)
    week_day = models.IntegerField(help_text="Comma-separated list of working days (1-7)")
    
    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name}"

class Appointment(models.Model):
    """Model for medical appointments between patients and doctors."""
    
    appointment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    start_time = models.TimeField()
    duration = '60'  # Fixed duration in minutes
    is_available = models.BooleanField(default=True)
    week_day = models.IntegerField(help_text="Comma-separated list of working days (1-7)")
    doctor_id = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    
    def __str__(self):
        return f"Dr. {self.doctor.last_name} - {self.get_week_day_display()} at {self.start_time}"
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(week_day__gte=1) & models.Q(week_day__lte=7),
                name='valid_week_day'
            )
        ]

class Booking(models.Model):
    """Model for booking appointments"""
    
    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment_id = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='bookings')
    patient_id = models.ForeignKey('users.Patient', on_delete=models.CASCADE, related_name='bookings')
    created_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_canceled = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if self.is_canceled:
            self.appointment.is_available = True
        else:
            self.appointment.is_available = False
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Appointment {self.booking_id} on {self.appointment_id.date} at {self.appointment_id.start_time}"
