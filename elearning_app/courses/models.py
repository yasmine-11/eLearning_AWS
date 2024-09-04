from django.db import models
from django.conf import settings

class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses')
    deadline = models.DateField(null=True, blank=True)

    class Meta:
        permissions = [
            ("can_manage_courses", "Can manage courses"),
        ]

    def __str__(self):
        return self.name

class CourseMaterial(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='course_materials/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Material for {self.course.name} uploaded at {self.uploaded_at}"

class Feedback(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='feedback')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ("can_leave_feedback", "Can leave feedback"),
        ]

    def __str__(self):
        return f'Feedback by {self.student} on {self.course}'

class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    is_blocked = models.BooleanField(default=False)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student} enrolled in {self.course}'
