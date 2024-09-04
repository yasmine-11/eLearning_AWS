from django.urls import path 
from . import consumers 


websocket_urlpatterns = [ 
    path('ws/course/<str:room_name>/', consumers.CourseChatConsumer.as_asgi()),
]
