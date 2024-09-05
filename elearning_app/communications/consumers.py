import json 
from channels.generic.websocket import AsyncWebsocketConsumer 
from asgiref.sync import sync_to_async
from .models import ChatMessage
from django.contrib.auth import get_user_model
from courses.models import Course
import time
import os
from django.conf import settings

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
        data = json.loads(text_data)
        message = data['message']
        file_data = data.get('file', None)

        file_url = ''
        if file_data:
            try:
                file_name = f"chat_files/{self.user.username}_{int(time.time())}_{file_data['name']}"
                file_path = os.path.join(settings.MEDIA_ROOT, file_name)

                # Save the file
                with open(file_path, "wb") as f:
                    f.write(bytearray(file_data['content']))

                file_url = f"{settings.MEDIA_URL}{file_name}"
            except Exception as e:
                print(f"Error saving file: {e}")

        await self.save_message(self.user, message, file_url, file_data['name'] if file_data else '')

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'file_url': file_url,
                'file_name': file_data['name'] if file_data else '',
                'username': self.user.username,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        file_url = event.get('file_url', '')
        file_name = event.get('file_name', '')
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'file_url': file_url,
            'file_name': file_name,
            'username': username,
        }))

    @sync_to_async
    def save_message(self, user, message, file_url, file_name):
        relative_path = file_url.replace(settings.MEDIA_URL, '') if file_url else None

        ChatMessage.objects.create(
            user=user,
            course=Course.objects.get(id=int(self.room_name.split('_')[1])),
            message=message,
            file=relative_path if user.user_type == 'teacher' else None
        )
        return message
