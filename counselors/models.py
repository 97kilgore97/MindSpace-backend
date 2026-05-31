from django.db import models
from django.conf import settings


class Counselor(models.Model):
    STATUS_CHOICES = [('online', 'Online'), ('busy', 'Busy'), ('offline', 'Offline')]

    full_name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to='counselors/', null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    is_verified = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class TimeSlot(models.Model):
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE, related_name='time_slots')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.counselor.full_name} — {self.start_time}"


class Session(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sessions')
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE, related_name='sessions')
    scheduled_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} with {self.counselor.full_name} at {self.scheduled_at}"
