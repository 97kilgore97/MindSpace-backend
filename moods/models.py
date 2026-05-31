from django.db import models
from django.conf import settings

class MoodLog(models.Model):
    SCORE_CHOICES = [(i, i) for i in range(1, 6)]
    user      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mood_logs')
    score     = models.IntegerField(choices=SCORE_CHOICES)
    note      = models.TextField(blank=True)
    logged_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.score} on {self.logged_at.date()}"


class JournalEntry(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='journal_entries')
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} journal on {self.created_at.date()}"