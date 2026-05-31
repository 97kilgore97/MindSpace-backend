import uuid
from django.db import models
from django.conf import settings


class CrisisFlag(models.Model):
    SEVERITY_CHOICES = [
        ('low',      'Low'),
        ('medium',   'Medium'),
        ('high',     'High'),
        ('critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('open',     'Open'),
        ('assigned', 'Assigned'),
        ('resolved', 'Resolved'),
    ]
    SOURCE_CHOICES = [
        ('chat',    'Peer Chat'),
        ('journal', 'Journal'),
        ('manual',  'Manual'),
    ]

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user         = models.ForeignKey(
                       settings.AUTH_USER_MODEL,
                       on_delete=models.SET_NULL,
                       null=True, blank=True,
                       related_name='crisis_flags'
                   )
    source       = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    source_id    = models.UUIDField(null=True, blank=True)
    trigger_text = models.TextField(max_length=500)
    severity     = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    status       = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    assigned_to  = models.ForeignKey(
                       'counselors.Counselor',
                       on_delete=models.SET_NULL,
                       null=True, blank=True,
                       related_name='assigned_flags'
                   )
    resolved_at  = models.DateTimeField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'CrisisFlag [{self.severity}] {self.user} — {self.status}'


class SMSLog(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('sent',      'Sent'),
        ('delivered', 'Delivered'),
        ('failed',    'Failed'),
    ]
    TYPE_CHOICES = [
        ('alert',        'Alert'),
        ('reminder',     'Reminder'),
        ('crisis',       'Crisis'),
        ('confirmation', 'Confirmation'),
    ]

    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient     = models.CharField(max_length=20)
    message       = models.TextField()
    type          = models.CharField(max_length=20, choices=TYPE_CHOICES, default='alert')
    status        = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    at_message_id = models.CharField(max_length=100, blank=True)
    sent_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f'SMS [{self.type}] → {self.recipient} ({self.status})'
