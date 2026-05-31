
# ── urls.py ───────────────────────────────────────────────
from django.urls import path
from . import views as v

urlpatterns = [
    path('',                    v.MoodLogListCreateView.as_view(),  name='mood-list'),
    path('summary/',            v.MoodSummaryView.as_view(),        name='mood-summary'),
    path('journal/',            v.JournalListCreateView.as_view(),  name='journal-list'),
    path('journal/<uuid:pk>/',  v.JournalDetailView.as_view(),      name='journal-detail'),
]
