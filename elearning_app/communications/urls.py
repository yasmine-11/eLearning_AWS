from django.urls import path
from .views import *

urlpatterns = [
    path('notifications/', notifications_view, name='notifications'),
    path('upload_chat_file/<int:course_id>/', upload_chat_file, name='upload_chat_file'),
]
