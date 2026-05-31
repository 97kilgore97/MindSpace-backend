"""
library/models.py — supports both manga (MangaDex) and books (Gutenberg)
with per-user content preference.
"""
import uuid
from django.db import models
from django.conf import settings

UNLOCK_CHOICES = [
    ('chapter_1',    '3-day streak'),
    ('chapter_2',    '7-day streak'),
    ('chapter_3',    '14-day streak'),
    ('second_book',  '21-day streak'),
    ('full_library', '30-day streak'),
]

CONTENT_TYPE_CHOICES = [('manga', 'Manga'), ('book', 'Book')]
PREFERENCE_CHOICES   = [('manga', 'Manga'), ('book', 'Books'), ('both', 'Both')]


class MangaTitle(models.Model):
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mangadex_id   = models.CharField(max_length=100, unique=True)
    title         = models.CharField(max_length=200)
    description   = models.TextField()
    cover_color   = models.CharField(max_length=20, default='#1a1a2e')
    unlock_key    = models.CharField(max_length=20, choices=UNLOCK_CHOICES)
    order         = models.PositiveIntegerField(default=0)
    is_active     = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class Book(models.Model):
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gutenberg_id  = models.IntegerField(unique=True)
    title         = models.CharField(max_length=200)
    author        = models.CharField(max_length=200)
    description   = models.TextField()
    cover_color   = models.CharField(max_length=20, default='#c06030')
    unlock_key    = models.CharField(max_length=20, choices=UNLOCK_CHOICES)
    order         = models.PositiveIntegerField(default=0)
    is_active     = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.title} — {self.author}'


class ReadingProgress(models.Model):
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reading_progress')
    content_type  = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES)
    content_id    = models.CharField(max_length=100)   # gutenberg_id or mangadex_id
    scroll_pct    = models.FloatField(default=0)
    last_page     = models.IntegerField(default=1)     # for books: page number; manga: chapter index
    last_read     = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'content_type', 'content_id']


class UserContentPreference(models.Model):
    user       = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='content_preference')
    preference = models.CharField(max_length=10, choices=PREFERENCE_CHOICES, default='both')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} prefers {self.preference}'
