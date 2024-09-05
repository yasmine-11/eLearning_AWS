from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import *
from communications.models import ChatMessage
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from users.models import User


@login_required
def course_detail(request, course_id):
    # select_related to preload the teacher's related data
    course = get_object_or_404(Course.objects.select_related('teacher'), id=course_id)
    course_materials = CourseMaterial.objects.filter(course=course) # Filter materials by course
    course_feedbacks = Feedback.objects.filter(course=course)  # Fetch feedbacks for the course

    materials = []
    for material in course_materials:
        file_type = None
        if material.file.name.endswith(".pdf"):
            file_type = "pdf"
        elif material.file.name.endswith((".jpg", ".jpeg", ".png")):
            file_type = "image"
        elif material.file.name.endswith(".mp4"):
            file_type = "video"
        else:
            file_type = "other"

        materials.append({
            'title': material.title,
            'uploaded_at': material.uploaded_at,
            'file_url': material.file.url,
            'file_type': file_type
        })

    if request.user.user_type == 'teacher':
        can_upload_materials = course.teacher == request.user
        enrolled_students = Enrollment.objects.filter(course=course).select_related('student')  # Get all enrolled students
    else:
        can_upload_materials = False
        enrolled_students = []

    if request.user.user_type == 'student':
        is_enrolled = Enrollment.objects.filter(course=course, student=request.user).exists()
    else:
        is_enrolled = False

    chat_messages = ChatMessage.objects.filter(course=course).order_by('timestamp')
    can_access_chat = request.user == course.teacher or is_enrolled # Check for chat access

    context = {
        'course': course,
        'materials': materials,
        'can_upload_materials': can_upload_materials,
        'is_enrolled': is_enrolled,
        'feedbacks': course_feedbacks,
        'enrolled_students': enrolled_students,
        'chat_room_name': f'course_{course.id}_chat',  # Chat room ID
        'chat_messages': chat_messages,
        'can_access_chat': can_access_chat,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
@permission_required('courses.can_manage_courses')
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            return redirect('home')
    else:
        form = CourseForm()
    return render(request, 'courses/create_course.html', {'form': form})

@login_required
@permission_required('courses.can_manage_courses')
def upload_material(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        form = CourseMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course
            material.save()
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseMaterialForm()

    return render(request, 'courses/upload_material.html', {'form': form, 'course': course})

@login_required
def enroll_in_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Check if the student is already enrolled and blocked
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course
    )
    if not enrollment.is_blocked:
        # If not blocked, add student to the course
        if created:
            enrollment.save()
    
    return redirect('course_detail', course_id=course.id)

@login_required
def leave_feedback(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = request.user
            feedback.course = course    
            feedback.save()
            return redirect('course_detail', course_id=course_id)
    else:
        form = FeedbackForm(initial={'course': course.id})  # Initialize the course field

    return render(request, 'courses/feedback_form.html', {'form': form, 'course': course})

@login_required
@permission_required('courses.can_manage_courses')
def remove_student(request, course_id, student_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Check if the logged-in user is the teacher of the course
    if course.teacher != request.user:
        return HttpResponseForbidden("You do not have permission to remove students from this course.")
    
    # Remove the student from the course
    enrollment = get_object_or_404(Enrollment, course=course, student_id=student_id)
    enrollment.delete()
    
    return redirect('course_detail', course_id=course_id)

@login_required
@permission_required('courses.can_manage_courses')
def block_student(request, course_id, student_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Ensure the user is the teacher of the course
    if course.teacher != request.user:
        return HttpResponseForbidden("You do not have permission to block students from this course.")
    
    # Block the student
    User = get_user_model()
    student = get_object_or_404(User, id=student_id)
    enrollment, created = Enrollment.objects.get_or_create(
        student=student,
        course=course
    )
    enrollment.is_blocked = True
    enrollment.save()
    
    return redirect('course_detail', course_id=course_id)

@login_required
@permission_required('courses.can_manage_courses')
def unblock_student(request, course_id, student_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Ensure the user is the teacher of the course
    if course.teacher != request.user:
        return HttpResponseForbidden("You do not have permission to unblock students from this course.")
    
    # Unblock the student
    User = get_user_model()
    student = get_object_or_404(User, id=student_id)
    enrollment, created = Enrollment.objects.get_or_create(
        student=student,
        course=course
    )
    enrollment.is_blocked = False
    enrollment.save()
    
    return redirect('course_detail', course_id=course_id)

