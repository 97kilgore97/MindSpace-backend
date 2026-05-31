from django.urls import path
from . import views

urlpatterns = [
    path('',                        views.SupportGroupListView.as_view(),  name='group-list'),
    path('<int:pk>/join/',          views.JoinGroupView.as_view(),         name='group-join'),
    path('<int:pk>/leave/',         views.LeaveGroupView.as_view(),        name='group-leave'),
    path('<int:pk>/messages/',      views.GroupMessageListView.as_view(),  name='group-messages'),
]