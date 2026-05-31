from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from core.ussd import ussd_callback


def health_check(request):
    return JsonResponse({'status': 'ok', 'service': 'MindSpace API'})


urlpatterns = [
    # Health
    path('',            health_check),
    path('health/',     health_check),

    # Admin panel
    path('admin/',      admin.site.urls),

    # REST API
    path('api/users/',          include('users.urls')),
    path('api/counselors/',     include('counselors.urls')),
    path('api/moods/',          include('moods.urls')),
    path('api/groups/',         include('groups.urls')),
    path('api/resources/',      include('resources.urls')),
    path('api/library/', include('library.urls')),

    # Africa's Talking USSD webhook
    path('api/ussd/',           ussd_callback),
]
