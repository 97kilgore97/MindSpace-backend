# ── views.py ──────────────────────────────────────────────
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Avg
from datetime import timedelta

from .models import MoodLog, JournalEntry
from .serializers import MoodLogSerializer, JournalEntrySerializer, MoodSummarySerializer


class MoodLogListCreateView(generics.ListCreateAPIView):
    """GET /api/moods/       — list mood logs
       POST /api/moods/      — log today's mood"""
    serializer_class = MoodLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MoodLog.objects.filter(
            user=self.request.user
        ).order_by('-logged_at')[:90]  # last 90 days


class MoodSummaryView(APIView):
    """GET /api/moods/summary/ — aggregated mood data for dashboard."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        logs = MoodLog.objects.filter(user=user)
        today = timezone.now().date()

        avg = logs.aggregate(avg=Avg('score'))['avg'] or 0

        # Weekly breakdown (last 7 days)
        weekly = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            entry = logs.filter(logged_at__date=day).first()
            weekly.append({
                'date': str(day),
                'day': day.strftime('%a'),
                'score': entry.score if entry else None,
                'label': {5: 'Great', 4: 'Good', 3: 'Okay', 2: 'Low', 1: 'Hard'}.get(
                    entry.score, None
                ) if entry else None,
            })

        # Streak: consecutive days with a log
        streak = 0
        check_day = today
        while logs.filter(logged_at__date=check_day).exists():
            streak += 1
            check_day -= timedelta(days=1)

        return Response({
            'average_score': round(avg, 1),
            'total_entries': logs.count(),
            'streak_days': streak,
            'weekly': weekly,
        })


class JournalListCreateView(generics.ListCreateAPIView):
    """GET /api/moods/journal/    — list journal entries
       POST /api/moods/journal/   — create a new entry"""
    serializer_class = JournalEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JournalEntry.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


class JournalDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/moods/journal/<id>/ — single journal entry."""
    serializer_class = JournalEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user)

