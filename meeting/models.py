import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Meeting(models.Model):
    """
    Meeting model representing a scheduled meeting event.
    
    Requirements: 1.1, 1.2, 2.1, 2.2
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['start_time']),
            models.Index(fields=['end_time']),
        ]
    
    def clean(self):
        """
        Validate that end_time is after start_time.
        Requirement: 1.2
        """
        super().clean()
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError({
                    'end_time': 'End time must be after start time'
                })
    
    def save(self, *args, **kwargs):
        """Override save to call full_clean for validation."""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} ({self.start_time} - {self.end_time})"


class Participant(models.Model):
    """
    Participant model representing a meeting attendee.
    
    Requirements: 2.1, 2.2
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    email = models.EmailField()
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Ensure unique participant per meeting (prevent duplicates)
        # Requirement: 2.2
        unique_together = [['meeting', 'email']]
        indexes = [
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.email}) - {self.meeting.title}"
