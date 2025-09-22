from django.urls import path
from . import consumers,consumers2

websocket_urlpatterns = [
    # re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),

    path("ws/chat/<int:sender_id>/<int:receiver_id>/",consumers.ChatConsumer.as_asgi()),
    path("ws/search-friends/<int:sender_id>/",consumers2.SearchFriend.as_asgi()),
    path("ws/add-friend/<int:sender_id>/<int:receiver_id>/",consumers2.AddFriend.as_asgi()),
    path("ws/notifications/<int:sender_id>/",consumers2.Notification.as_asgi()),
    path("ws/accept-reject/<int:sender_id>/<int:receiver_id>/<str:checker>/",consumers2.AcceptFriendRequest.as_asgi()),
]
