from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Auth
    path('register/',           views.RegisterView.as_view(),        name='user-register'),
    path('anonymous/',          views.AnonymousLoginView.as_view(),   name='user-anonymous'),
    path('login/',              views.LoginView.as_view(),            name='user-login'),
    path('logout/',             views.LogoutView.as_view(),           name='user-logout'),
    path('token/refresh/',      TokenRefreshView.as_view(),           name='token-refresh'),

    # Own profile
    path('me/',                 views.MeView.as_view(),               name='user-me'),
    path('me/profile/',         views.ProfileView.as_view(),          name='user-profile'),
    path('change-password/',    views.ChangePasswordView.as_view(),   name='change-password'),

    # Admin
    path('',                    views.UserListView.as_view(),         name='user-list'),
    path('<uuid:pk>/',          views.UserDetailView.as_view(),       name='user-detail'),
    path('<uuid:pk>/flag/',     views.flag_user,                      name='user-flag'),
]
