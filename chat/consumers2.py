import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
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



