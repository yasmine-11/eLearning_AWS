from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import *
from courses.models import Course
from django.views.decorators.csrf import csrf_exempt

@login_required
def notifications_view(request):
    notifications = request.user.notifications.order_by('-created_at')
    # Mark notifications as read after fetching them
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'communications/notifications.html', {'notifications': notifications})

