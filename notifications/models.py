from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid


class Notification(models.Model):
    """Model for storing user notifications"""
    
    # Notification status choices
    UNREAD = 'unread'
    READ = 'read'
    ARCHIVED = 'archived'
    
    STATUS_CHOICES = [
        (UNREAD, _('Unread')),
        (READ, _('Read')),
        (ARCHIVED, _('Archived')),
    ]
    
    # Notification type choices
    APPOINTMENT_BOOK = 'book'
    APPOINTMENT_CANCEL = 'cancel'
    APPOINTMENT_RESCHEDULE = 'reschedule'
    APPOINTMENT_REMINDER = 'appointment_reminder'
    SYSTEM_NOTIFICATION = 'system_notification'
    
    TYPE_CHOICES = [
        (APPOINTMENT_BOOK, _('Appointment Booked')),
        (APPOINTMENT_CANCEL, _('Appointment Cancelled')),
        (APPOINTMENT_RESCHEDULE, _('Appointment Rescheduled')),
        (APPOINTMENT_REMINDER, _('Appointment Reminder')),
        (SYSTEM_NOTIFICATION, _('System Notification')),
    ]
    
    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    appointment_id = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=UNREAD)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read_at = models.DateTimeField(null=True, blank=True)

    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment_id = models.ForeignKey('appointments.Appointment', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    type_id = models.ForeignKey('NotificationType', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient']),
            models.Index(fields=['status']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['appointment_id']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} for {self.recipient} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if self.status == self.UNREAD:
            self.status = self.READ
            self.read_at = timezone.now()
            self.save()
    
    def archive(self):
        """Archive notification"""
        self.status = self.ARCHIVED
        self.save()
    
    @classmethod
    def create_appointment_notification(cls, appointment, notification_type):
        """Create appointment notification"""
        if notification_type == cls.APPOINTMENT_BOOK:
            title = "Appointment Booked"
            message = f"Your appointment with Dr. {appointment.doctor.last_name} on {appointment.date} at {appointment.availability.start_time} has been booked."
        elif notification_type == cls.APPOINTMENT_RESCHEDULE:
            title = "Appointment Rescheduled"
            message = f"Your appointment with Dr. {appointment.doctor.last_name} has been rescheduled to {appointment.date} at {appointment.availability.start_time}."
        elif notification_type == cls.APPOINTMENT_CANCEL:
            title = "Appointment Cancelled"
            message = f"Your appointment with Dr. {appointment.doctor.last_name} on {appointment.date} at {appointment.availability.start_time} has been cancelled."
        else:
            title = "Appointment Reminder"
            message = f"Reminder: Your appointment with Dr. {appointment.doctor.last_name} is scheduled for {appointment.date} at {appointment.availability.start_time}."
        
        return cls.objects.create(
            recipient=appointment.patient.user,
            title=title,
            message=message,
            notification_type=notification_type,
            appointment_id=str(appointment.appointment_id)
        )
        

class NotificationTemplate(models.Model):
    """Model for notification templates"""
    
    # Template type choices
    APPOINTMENT_REMINDER = 'appointment_reminder'
    APPOINTMENT_CONFIRMATION = 'appointment_confirmation'
    APPOINTMENT_CANCELLATION = 'appointment_cancellation'
    
    TEMPLATE_TYPE_CHOICES = [
        (APPOINTMENT_REMINDER, _('Appointment Reminder')),
        (APPOINTMENT_CONFIRMATION, _('Appointment Confirmation')),
        (APPOINTMENT_CANCELLATION, _('Appointment Cancellation')),
    ]
    
    name = models.CharField(max_length=100, default="Default Template")
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPE_CHOICES, default=APPOINTMENT_REMINDER)
    content = models.TextField(help_text=_("Use {patient_name}, {doctor_name}, {date}, {time}, etc. as placeholders"), default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['template_type', 'is_active']
        indexes = [
            models.Index(fields=['template_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"


class AppointmentReminder(models.Model):
    """Model for appointment reminders"""
    
    # Reminder status choices
    PENDING = 'pending'
    SENT = 'sent'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, _('Pending')),
        (SENT, _('Sent')),
        (FAILED, _('Failed')),
        (CANCELLED, _('Cancelled')),
    ]
    
    appointment_id = models.CharField(max_length=50)
    recipient = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='appointment_reminders')
    message = models.TextField()
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=PENDING)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_time']
        indexes = [
            models.Index(fields=['appointment_id']),
            models.Index(fields=['recipient']),
            models.Index(fields=['status']),
            models.Index(fields=['scheduled_time']),
        ]
    
    def __str__(self):
        return f"Reminder for {self.appointment_id} to {self.recipient}"
    
    def mark_as_sent(self):
        """Mark reminder as sent"""
        self.status = self.SENT
        self.sent_at = timezone.now()
        self.save()
    
    def mark_as_failed(self):
        """Mark reminder as failed"""
        self.status = self.FAILED
        self.save()
    
    def cancel(self):
        """Cancel reminder"""
        self.status = self.CANCELLED
        self.save()
    
    def schedule_reminder_notification(self, appointment):
        """Schedule a reminder notification for the appointment"""
        # Calculate reminder time (24 hours before appointment)
        appointment_datetime = timezone.datetime.combine(
            appointment.date, 
            appointment.availability.start_time, 
            tzinfo=timezone.get_current_timezone()
        )
        reminder_time = appointment_datetime - timezone.timedelta(days=1)
        
        # Create the reminder with scheduled time
        return AppointmentReminder.objects.create(
            appointment_id=str(appointment.appointment_id),
            recipient=appointment.patient.user,
            message=f"Reminder: Your appointment with Dr. {appointment.doctor.last_name} is tomorrow at {appointment.availability.start_time}.",
            scheduled_time=reminder_time
        )
