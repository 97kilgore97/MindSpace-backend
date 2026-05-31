from django.urls import path
from . import views

urlpatterns = [
    # Public / user
    path('',                                    views.CounselorListView.as_view(),          name='counselor-list'),
    path('<uuid:pk>/',                          views.CounselorDetailView.as_view(),        name='counselor-detail'),
    path('<uuid:pk>/slots/',                    views.CounselorTimeSlotsView.as_view(),     name='counselor-slots'),
    path('book/',                               views.BookSessionView.as_view(),            name='book-session'),
    path('my-sessions/',                        views.MySessionsView.as_view(),             name='my-sessions'),
    path('sessions/<uuid:pk>/',                 views.SessionDetailView.as_view(),          name='session-detail'),
    path('sessions/<uuid:pk>/cancel/',          views.CancelSessionView.as_view(),          name='cancel-session'),

    # Admin
    path('admin/',                              views.AdminCounselorManageView.as_view(),   name='admin-counselors'),
    path('admin/sessions/',                     views.AllSessionsView.as_view(),            name='admin-sessions'),
    path('<uuid:pk>/status/',                   views.set_counselor_status,                 name='counselor-status'),
]
