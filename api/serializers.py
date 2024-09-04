from rest_framework import serializers
from users.models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'real_name', 'photo', 'user_type']

class StatusUpdateSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')  # To include username

    class Meta:
        model = StatusUpdate
        fields = ['id', 'username', 'content', 'created_at']
        read_only_fields = ['username', 'created_at']
