from django.urls import re_path, path

from . import consumers

websocket_urlpatterns = [
    # re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    # re_path('', consumers.LiveConsumer.as_asgi()),
    path('chat/socket/<str:room_name>/', consumers.ChatConsumer.as_asgi()),
    path('chat/socket/', consumers.FirstConsumer.as_asgi()),
]
