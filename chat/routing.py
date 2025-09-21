from django.urls import path
from . import consumers,consumers2

websocket_urlpatterns = [
    # re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),

    path("ws/chat/<int:sender_id>/<int:receiver_id>/",consumers.ChatConsumer.as_asgi()),
    path("ws/search-friends/<int:sender_id>/",consumers2.SearchFriend.as_asgi()),
]
