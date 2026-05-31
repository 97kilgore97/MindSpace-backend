from django.urls import path
from . import views

urlpatterns = [
    path('',                                views.LibraryListView.as_view(),    name='library-list'),
    path('streak/',                         views.StreakView.as_view(),         name='streak'),
    path('preference/',                     views.SetPreferenceView.as_view(),  name='library-preference'),
    path('progress/',                       views.SaveProgressView.as_view(),   name='save-progress'),
    path('progress/get/',                   views.GetProgressView.as_view(),    name='get-progress'),
    path('book/<int:gutenberg_id>/read/',   views.BookContentView.as_view(),    name='book-read'),
    path('manga/<str:mangadex_id>/check/',  views.MangaCheckView.as_view(),     name='manga-check'),
]
