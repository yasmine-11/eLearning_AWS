from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import *
from .models import *
from courses.models import *
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from communications.models import Notification

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
             user = form.save(commit=False) 
            user.username = user.username.lower()  # Convert the username to lowercase
            user.save()

            user_type = form.cleaned_data.get('user_type')

            # Automatically add the user to the appropriate group
            if user_type == 'teacher':
                group = Group.objects.get(name='Teachers')
                group.user_set.add(user)  # Add the user to the group
                print("teacher added to the group successfuly")
            elif user_type == 'student':
                group = Group.objects.get(name='Students')
                group.user_set.add(user)  # Add the user to the group
                print("Student added to the group successfuly")

            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            # If the form is not valid, it will return to the template with errors
            return render(request, 'users/login.html', {'form': form})
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    user = request.user
    if user.user_type == 'teacher':
        # Fetch courses, status updates and students
        courses = Course.objects.filter(teacher=user)
        status_updates = user.statusupdate_set.all()
        students = User.objects.filter(user_type='student')
        
        context = {
            'user': user,
            'courses': courses,
            'status_updates': status_updates,
            'students': students,
        }
        return render(request, 'users/teacher_home.html', context)
    elif user.user_type == 'student':
        # Fetch courses the student is enrolled in
        enrolled_courses = Course.objects.filter(
            enrollments__student=user, 
            enrollments__is_blocked=False
        )
        status_updates = user.statusupdate_set.all()
        available_courses = Course.objects.exclude(enrollments__student=user)
        unread_notifications_count = request.user.notifications.filter(is_read=False).count()
        context = {
            'user': user,
            'enrolled_courses': enrolled_courses,
            'status_updates': status_updates,
            'available_courses': available_courses,
            'unread_notifications_count': unread_notifications_count,
        }
        return render(request, 'users/student_home.html', context)
    else:
        return redirect('login')

@login_required
def user_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    # Fetch the status updates for the profile user
    status_updates = profile_user.statusupdate_set.all()

    # Fetch courses associated with the profile user if they are a teacher
    if profile_user.user_type == 'teacher':
        courses = Course.objects.filter(teacher=profile_user)
    else:
        courses = None  # Students don't have associated courses to show here

    # Fetch enrolled courses if user is a student
    if profile_user.user_type == 'student':
        enrolled_courses = Course.objects.filter(
            enrollments__student=profile_user, 
            enrollments__is_blocked=False
        )
    else:
        enrolled_courses = None

    context = {
        'profile_user': profile_user,
        'status_updates': status_updates,
        'courses': courses,
        'enrolled_courses': enrolled_courses,
    }
    return render(request, 'users/user_profile.html', context)


@login_required
def status_update(request):
    if request.method == 'POST':
        form = StatusUpdateForm(request.POST)
        if form.is_valid():
            status = form.save(commit=False)
            status.user = request.user
            status.save()
            return redirect('home')
    else:
        form = StatusUpdateForm()
    return render(request, 'users/status_update.html', {'form': form})

@login_required
def search_profiles(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        # If the user is a teacher, search for both students and teachers
        if request.user.user_type == 'teacher':
            results = User.objects.filter(
                Q(real_name__icontains=query) | Q(username__icontains=query)
            )

        # If the user is a student, search for students only
        elif request.user.user_type == 'student':
            results = User.objects.filter(
                Q(real_name__icontains=query) | Q(username__icontains=query),
                user_type='student'
            )

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'users/search_results.html', context)
