from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    REAL_NAME_MAX_LENGTH = 100
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )

    real_name = models.CharField(max_length=REAL_NAME_MAX_LENGTH)
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)
    user_type = models.CharField(max_length=7, choices=USER_TYPE_CHOICES)

    class Meta:
        permissions = [
            ("can_post_status_update", "Can post status update"),
        ]

    def __str__(self):
        return self.username

class StatusUpdate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at} - {self.content[:30]}"