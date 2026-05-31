
# ─────────────────────────────────────────────────────────────
# library/serializers.py
# ─────────────────────────────────────────────────────────────
from rest_framework import serializers
from .models import MangaTitle, Book

class MangaTitleSerializer(serializers.ModelSerializer):
    is_unlocked  = serializers.SerializerMethodField()
    progress_pct = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()

    class Meta:
        model  = MangaTitle
        fields = ['id', 'mangadex_id', 'title', 'description', 'cover_color',
                  'unlock_key', 'order', 'is_unlocked', 'progress_pct', 'content_type']

    def get_is_unlocked(self, obj):
        return obj.unlock_key in self.context.get('milestones', [])

    def get_progress_pct(self, obj):
        return self.context.get('progress_map', {}).get(f'manga_{obj.mangadex_id}', 0)

    def get_content_type(self, obj):
        return 'manga'


class BookSerializer(serializers.ModelSerializer):
    is_unlocked  = serializers.SerializerMethodField()
    progress_pct = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()

    class Meta:
        model  = Book
        fields = ['id', 'gutenberg_id', 'title', 'author', 'description', 'cover_color',
                  'unlock_key', 'order', 'is_unlocked', 'progress_pct', 'content_type']

    def get_is_unlocked(self, obj):
        return obj.unlock_key in self.context.get('milestones', [])

    def get_progress_pct(self, obj):
        return self.context.get('progress_map', {}).get(f'book_{obj.gutenberg_id}', 0)

    def get_content_type(self, obj):
        return 'book'

