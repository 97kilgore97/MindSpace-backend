from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from .models import MoodEntry
from .serializers import MoodEntrySerializer

class MoodEntryViewSet(viewsets.ModelViewSet):
    serializer_class = MoodEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MoodEntry.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
