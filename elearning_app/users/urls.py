from django.urls import path, include
from .views import *

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('', home, name='home'),  # Home page
    path('status_update/', status_update, name='status_update'),
    path('search/', search_profiles, name='search_profiles'),
    path('profile/<int:user_id>/', user_profile, name='user_profile'),
]
