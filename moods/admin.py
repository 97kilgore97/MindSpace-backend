from django.contrib import admin
from .models import MoodLog, JournalEntry

admin.site.register(MoodLog)
admin.site.register(JournalEntry)
