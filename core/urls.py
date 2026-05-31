from rest_framework.routers import DefaultRouter
from .views import MoodEntryViewSet

router = DefaultRouter()
router.register(r'moods', MoodEntryViewSet, basename='mood')

urlpatterns = router.urls
