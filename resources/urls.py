

# ── urls.py ───────────────────────────────────────────────
from django.urls import path
import resources.views as rv

urlpatterns = [
    path('',                        rv.ResourceListView.as_view(),          name='resource-list'),
    path('categories/',             rv.ResourceCategoryListView.as_view(),  name='resource-categories'),
    path('<uuid:pk>/',              rv.ResourceDetailView.as_view(),        name='resource-detail'),
    path('admin/',                  rv.AdminResourceView.as_view(),         name='admin-resources'),
    path('admin/<uuid:pk>/',        rv.AdminResourceDetailView.as_view(),   name='admin-resource-detail'),
]
