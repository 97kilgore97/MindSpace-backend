from django.contrib import admin
from .models import Counselor, Session, TimeSlot

@admin.register(Counselor)
class CounselorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'specialty', 'status', 'is_verified', 'rating']
    list_filter = ['status', 'is_verified']

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['counselor', 'start_time', 'end_time', 'is_booked']

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'counselor', 'scheduled_at', 'status']
    list_filter = ['status']
