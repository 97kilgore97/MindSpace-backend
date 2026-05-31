
# ─────────────────────────────────────────────────────────────
# library/views.py
# ─────────────────────────────────────────────────────────────
import requests
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import UserContentPreference, MangaTitle, Book, ReadingProgress
from .serializers import MangaTitleSerializer, BookSerializer

GUTENBERG_TEXT = 'https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt'


class LibraryListView(APIView):
    """
    GET /api/library/
    Returns manga and/or books based on user preference + streak unlock status.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from moods.streak import compute_streak
        streak_data = compute_streak(request.user)
        milestones  = streak_data['milestones']

        # Get user preference
        pref_obj, _ = UserContentPreference.objects.get_or_create(user=request.user)
        preference  = pref_obj.preference  # 'manga' | 'book' | 'both'

        # Build progress map
        progress_qs  = ReadingProgress.objects.filter(user=request.user)
        progress_map = {f'{p.content_type}_{p.content_id}': p.scroll_pct for p in progress_qs}
        ctx = {'milestones': milestones, 'progress_map': progress_map, 'request': request}

        manga, books = [], []

        if preference in ('manga', 'both'):
            manga_qs = MangaTitle.objects.filter(is_active=True)
            manga = MangaTitleSerializer(manga_qs, many=True, context=ctx).data

        if preference in ('book', 'both'):
            book_qs = Book.objects.filter(is_active=True)
            books = BookSerializer(book_qs, many=True, context=ctx).data

        return Response({
            'streak':     streak_data,
            'preference': preference,
            'manga':      manga,
            'books':      books,
        })


class SetPreferenceView(APIView):
    """POST /api/library/preference/  — { preference: 'manga'|'book'|'both' }"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        pref = request.data.get('preference')
        if pref not in ('manga', 'book', 'both'):
            return Response({'error': 'preference must be manga, book, or both.'}, status=400)
        obj, _ = UserContentPreference.objects.get_or_create(user=request.user)
        obj.preference = pref
        obj.save()
        return Response({'preference': pref})


class SaveProgressView(APIView):
    """POST /api/library/progress/  — { content_id, content_type, scroll_pct, last_page }"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        content_id   = request.data.get('content_id')
        content_type = request.data.get('content_type')
        scroll_pct   = float(request.data.get('scroll_pct', 0))
        last_page    = int(request.data.get('last_page', 1))

        if content_type not in ('manga', 'book'):
            return Response({'error': 'content_type must be manga or book.'}, status=400)

        progress, _ = ReadingProgress.objects.update_or_create(
            user=request.user, content_type=content_type, content_id=str(content_id),
            defaults={'scroll_pct': min(100, max(0, scroll_pct)), 'last_page': last_page}
        )
        return Response({'scroll_pct': progress.scroll_pct, 'last_page': progress.last_page})


class GetProgressView(APIView):
    """GET /api/library/progress/?content_id=&content_type="""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        content_id   = request.query_params.get('content_id')
        content_type = request.query_params.get('content_type')
        try:
            p = ReadingProgress.objects.get(user=request.user, content_type=content_type, content_id=content_id)
            return Response({'scroll_pct': p.scroll_pct, 'last_page': p.last_page})
        except ReadingProgress.DoesNotExist:
            return Response({'scroll_pct': 0, 'last_page': 1})


class BookContentView(APIView):
    """GET /api/library/book/<gutenberg_id>/read/?page=<n>"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, gutenberg_id):
        from moods.streak import compute_streak
        try:
            book = Book.objects.get(gutenberg_id=gutenberg_id, is_active=True)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found.'}, status=404)

        streak_data = compute_streak(request.user)
        if book.unlock_key not in streak_data['milestones']:
            days_map = {'chapter_1': 3, 'chapter_2': 7, 'chapter_3': 14, 'second_book': 21, 'full_library': 30}
            days_needed = days_map.get(book.unlock_key, 999)
            return Response({
                'error': 'Book not unlocked yet.',
                'streak_days': streak_data['streak_days'],
                'days_needed': days_needed,
                'days_to_go':  max(0, days_needed - streak_data['streak_days']),
            }, status=403)

        page     = int(request.query_params.get('page', 1))
        per_page = 3000

        try:
            resp = requests.get(GUTENBERG_TEXT.format(id=gutenberg_id), timeout=10)
            resp.raise_for_status()
            full_text = resp.text

            for m in ['*** START OF', '***START OF']:
                idx = full_text.find(m)
                if idx != -1:
                    full_text = full_text[full_text.find('\n', idx) + 1:]
                    break
            for m in ['*** END OF', '***END OF']:
                idx = full_text.find(m)
                if idx != -1:
                    full_text = full_text[:idx]
                    break

            full_text   = full_text.strip()
            total_pages = max(1, -(-len(full_text) // per_page))
            start  = (page - 1) * per_page
            chunk  = full_text[start:start + per_page]

            return Response({
                'title': book.title, 'author': book.author,
                'page': page, 'total_pages': total_pages,
                'content': chunk, 'has_next': page < total_pages, 'has_prev': page > 1,
            })
        except requests.RequestException as e:
            return Response({'error': f'Could not fetch book: {e}'}, status=502)


class MangaCheckView(APIView):
    """
    GET /api/library/manga/<mangadex_id>/check/
    Verify unlock status before frontend hits MangaDex directly.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, mangadex_id):
        from moods.streak import compute_streak
        try:
            manga = MangaTitle.objects.get(mangadex_id=mangadex_id, is_active=True)
        except MangaTitle.DoesNotExist:
            return Response({'error': 'Manga not found.'}, status=404)

        streak_data = compute_streak(request.user)
        unlocked = manga.unlock_key in streak_data['milestones']
        days_map = {'chapter_1': 3, 'chapter_2': 7, 'chapter_3': 14, 'second_book': 21, 'full_library': 30}
        days_needed = days_map.get(manga.unlock_key, 999)

        return Response({
            'unlocked':    unlocked,
            'streak_days': streak_data['streak_days'],
            'days_needed': days_needed,
            'days_to_go':  max(0, days_needed - streak_data['streak_days']) if not unlocked else 0,
        })


class StreakView(APIView):
    """GET /api/library/streak/"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from moods.streak import compute_streak
        return Response(compute_streak(request.user))
