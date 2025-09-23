import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.shortcuts import redirect
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from mako.testing.assertions import assert_raises_with_given_cause


class SearchFriend(AsyncWebsocketConsumer):

    @database_sync_to_async
    def get_user(self):
        from users.models import User
        return User.objects.filter(id=self.sender_id).first()

    async def connect(self):
        self.sender_id = self.scope["url_route"]["kwargs"]["sender_id"]
        self.group_name = f"searching_by_{self.sender_id}"


        self.user_obj = await self.get_user()






        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()
        print("connect")
    async def disconnect(self, code):

        await self.channel_layer.group_discard(self.group_name, self.channel_name)


    @database_sync_to_async
    def get_user_friends(self):
        return list(self.user_obj.friends.all())
    async def receive(self, text_data):
        data = json.loads(text_data)
        search_friend = data.get("search")

        if search_friend:

             friends = await  self.get_friends(search_friend)
             user_friends = await self.get_user_friends()
             friends_data = [{"user_id": i.id,"name": i.name,"icon": i.icon,"is_friend": i in user_friends} for i in friends]
             print(friends_data)
             await self.send(text_data=json.dumps({"friends":friends_data}))

        else:

            await self.send(text_data=json.dumps({"friends":[]}))





    @database_sync_to_async
    def get_friends(self,search_friend):

        from users.models import User

        return list(

            User.objects.filter(email__icontains = search_friend).exclude(id=self.sender_id)
        )



class AddFriend(AsyncWebsocketConsumer):

    async def connect(self):
        self.sender_id = self.scope["url_route"]["kwargs"]["sender_id"]
        self.receiver_id = self.scope["url_route"]["kwargs"]["receiver_id"]

        await self.accept()

        sender_obj = await self.get_user(self.sender_id)
        receiver_obj = await self.get_user(self.receiver_id)

        if not await self.check_friend_request(sender_obj, receiver_obj):
            x = await self.add_friend_request(sender_obj, receiver_obj)

            if x:
                # notify sender
                await self.send(json.dumps({
                    "type": "notify",
                    "message": f"You sent a friend request to {x.receiver.name}"
                }))

                # notify receiver
                await self.trigger_notifications(self.receiver_id)

            else:
                await self.send(json.dumps({
                    "type": "server_error",
                    "message": "Internal Server Error"
                }))
        else:
            await self.send(json.dumps({
                "type": "check_friend_request",
                "message": "You’ve already sent a request"
            }))

    @database_sync_to_async
    def check_friend_request(self, sender_obj, receiver_obj):
        from users.models import FriendRequests
        return FriendRequests.objects.filter(sender=sender_obj, receiver=receiver_obj).exists()

    @database_sync_to_async
    def get_user(self, user_id):
        from users.models import User
        return User.objects.filter(id=user_id).first()

    @database_sync_to_async
    def add_friend_request(self, sender_obj, receiver_obj):
        from users.models import FriendRequests
        return FriendRequests.objects.create(sender=sender_obj, receiver=receiver_obj)

    async def trigger_notifications(self, user_id):
        notifications = await self.get_notifications(user_id)
        await self.send_notifications(notifications, user_id)

    @database_sync_to_async
    def get_notifications(self, user_id):
        from users.models import FriendRequests

        friends = (
            FriendRequests.objects
            .filter(receiver=user_id)
            .select_related("sender")  # fetch sender in one query
            .order_by("created_at")
        )

        lst = []
        for friend in friends:
            lst.append({
                "user_id": friend.sender.id,
                "sender": friend.sender.name,
                "created_at": friend.created_at.isoformat(),
                "icon": friend.sender.icon
            })

        return lst


    async def send_notifications(self, notifications, user_id):
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"notification_{user_id}",
            {
                "type": "send_notification",
                "notification_messages": notifications
            }
        )


class Notification(AsyncWebsocketConsumer):



        async def connect(self):

            self.current_id = self.scope["url_route"]["kwargs"]["sender_id"]

            self.group_name = f"notification_{self.current_id}"
            await self.channel_layer.group_add(self.group_name,self.channel_name)

            await self.accept()

            await self.send(json.dumps(

                {
                    "type": "notification",
                    "message": await self.send_notifications_user(self.current_id)

                }
            ))


        async def disconnect(self, code):

            await self.channel_layer.group_discard(self.group_name,self.channel_name)


        async def send_notification(self,event):

            await self.send(json.dumps(

                {
                    "type":"notification",
                    "message": event["notification_messages"]
                }
            ))

        @database_sync_to_async
        def send_notifications_user(self, user_id):
            from users.models import FriendRequests
            objs = FriendRequests.objects.filter(receiver=user_id).order_by("created_at")
            return [
                {
                    "user_id": obj.sender.id,
                    "sender": obj.sender.name,
                    "icon":obj.sender.icon,
                    "created_at": obj.created_at.isoformat()
                }
                for obj in objs
            ]


class AcceptFriendRequest(AsyncWebsocketConsumer):

    async def connect(self):

        self.sender_id = self.scope["url_route"]["kwargs"]["sender_id"]
        self.receiver_id = self.scope["url_route"]["kwargs"]["receiver_id"]

        self.sender_obj = await self.get_user(self.sender_id)
        self.receiver_obj = await self.get_user(self.receiver_id)
        self.checker = self.scope["url_route"]["kwargs"]["checker"]

        await self.accept()

        await self.delete_friend_request(self.sender_obj,self.receiver_obj,self.checker)

        await self.send(json.dumps({

            "redirect_url": '/home/'
        }))


    @database_sync_to_async
    def get_user(self,user_id):
        from users.models import User
        return User.objects.filter(id=user_id).first()

    @database_sync_to_async
    def delete_friend_request(self,sender_obj,receiver_obj,checker):

        from users.models import FriendRequests

        if checker.lower() == 'true':
            sender_obj.friends.add(receiver_obj)

        FriendRequests.objects.filter(sender=sender_obj,receiver=receiver_obj).delete()

        print("deleted")
