from django.urls import path
from .views import *

urlpatterns = [
    path('notifications/', notifications_view, name='notifications'),
]
