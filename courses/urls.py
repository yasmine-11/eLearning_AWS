from django.urls import path
from .views import *

urlpatterns = [
    path('<int:course_id>/', course_detail, name='course_detail'),
    path('<int:course_id>/upload_material/', upload_material, name='upload_material'),  # URL for uploading material
    path('create_course/', create_course, name='create_course'),  # URL for creating a course
    path('<int:course_id>/enroll', enroll_in_course, name='enroll_in_course'), # URL for enrolling on a course
    path('<int:course_id>/feedback', leave_feedback, name='leave_feedback'), # URL to submit feedback for a course
    path('<int:course_id>/remove/<int:student_id>/', remove_student, name='remove_student'), # URL to remove students
    path('<int:course_id>/block/<int:student_id>/', block_student, name='block_student'), # URL to block students
    path('<int:course_id>/unblock/<int:student_id>/', unblock_student, name='unblock_student'), # URL to block students
]
