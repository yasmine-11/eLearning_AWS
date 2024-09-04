from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
from communications.models import Notification

@receiver(post_save, sender=Enrollment)
def notify_teacher_on_enrollment(sender, instance, created, **kwargs):
    if created:
        # Notify the teacher when a new student enrolls
        course = instance.course
        teacher = course.teacher
        student = instance.student
        Notification.objects.create(
            recipient=teacher,
            sender=student,
            course=course,
            message=f"{student.real_name} has enrolled in your course '{course.name}'."
        )

@receiver(post_save, sender=CourseMaterial)
def notify_students_on_material(sender, instance, created, **kwargs):
    if created:
        # Notify enrolled students when new material is added
        course = instance.course
        students = Enrollment.objects.filter(course=course, is_blocked=False).select_related('student')
        for enrollment in students:
            student = enrollment.student
            Notification.objects.create(
                recipient=student,
                sender=course.teacher,
                course=course,
                message=f"New material '{instance.title}' has been added to the course '{course.name}'."
            )
