import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmconnect.settings')
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from core.middleware import JWTAuthMiddlewareStack
from core.consumers import ChatConsumer

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': JWTAuthMiddlewareStack(
        URLRouter([
            re_path(r'^ws/chat/(?P<room_id>\d+)/$', ChatConsumer.as_asgi()),
        ])
    ),
})
