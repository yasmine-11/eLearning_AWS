import json 
from channels.generic.websocket import AsyncWebsocketConsumer 
from asgiref.sync import sync_to_async
from .models import ChatMessage
from django.contrib.auth import get_user_model
from courses.models import Course

User = get_user_model()

class CourseChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Store the user in the connection context
        self.user = self.scope['user']

        # Log the user who connected
        print(f"User connected: {self.user.username}")

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        file_url = text_data_json.get('file_url', '')

        # Save the message in the database
        await self.save_message(self.user, message, file_url)

        # Send message to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'file_url': file_url,
                'username': self.user.username,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        file_url = event.get('file_url', '')
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'file_url': file_url,
            'username': username,
        }))

    @sync_to_async
    def save_message(self, user, message, file_url):
        # Extract the relative path if full URL is provided
        relative_path = file_url.replace(settings.MEDIA_URL, '') if file_url else None

        ChatMessage.objects.create(
            user=user,
            course=Course.objects.get(id=int(self.room_name.split('_')[1])),
            message=message,
            file=relative_path if user.user_type == 'teacher' else None  # Only save file if the user is a teacher
        )

