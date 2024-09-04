from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import *
from courses.models import Course
from .forms import ChatMessageForm
from django.views.decorators.csrf import csrf_exempt

@login_required
def notifications_view(request):
    notifications = request.user.notifications.order_by('-created_at')
    # Mark notifications as read after fetching them
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'communications/notifications.html', {'notifications': notifications})

@login_required
def upload_chat_file(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        form = ChatMessageForm(request.POST, request.FILES)
        if form.is_valid():
            chat_message = form.save(commit=False)
            chat_message.user = request.user
            chat_message.course = course
            chat_message.save()

            return redirect('course_detail', course_id=course.id)

    return redirect('course_detail', course_id=course.id)

