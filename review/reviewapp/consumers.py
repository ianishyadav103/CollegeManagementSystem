import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"] #get room name
        self.room_group_name = "chat_%s" % self.room_name  #naming group
        self.user = self.scope["user"] #get user entered in name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        #Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket/Sender client
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        time = text_data_json["time"]

        ##send message to room (not to members)
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "chat_message",
                "message": message,
                "username": self.user.username,
                "time":time,
            }
        )

    #Receive message in room (not from members)
    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        time = event["time"]


        # Send message to WebSocket/ all clients (including sender)
        await self.send(text_data=json.dumps({
            "message": message,
            "username": username,
            "time": time,
        }))

        