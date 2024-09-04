import csv
from django.core.management.base import BaseCommand
from courses.models import *
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Seed courses and course materials from CSV files'

    def handle(self, *args, **kwargs):
        csv_files_dir = os.path.join(settings.BASE_DIR, 'csv_files')

        # Load courses
        courses_csv_path = os.path.join(csv_files_dir, 'courses.csv')
        with open(courses_csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Course.objects.create(
                    name=row['name'],
                    description=row['description'],
                    teacher_id=row['teacher_id'],
                    deadline=row['deadline']
                )

        # Load course materials
        materials_csv_path = os.path.join(csv_files_dir, 'materials.csv')
        with open(materials_csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                CourseMaterial.objects.create(
                    course_id=row['course_id'],
                    title=row['title'],
                    file=row['file']
                )
        # Load feedback
        feedback_csv_path = os.path.join(csv_files_dir, 'feedback.csv')
        with open(feedback_csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Feedback.objects.create(
                    course_id=row['course_id'],
                    student_id=row['student_id'],
                    comment=row['comment'],
                    created_at=row['created_at']
                )

        # Load enrollments
        enrollments_csv_path = os.path.join(csv_files_dir, 'enrollments.csv')
        with open(enrollments_csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Enrollment.objects.create(
                    course_id=row['course_id'],
                    student_id=row['student_id'],
                    is_blocked=row['is_blocked'] == 'TRUE',  # Convert to boolean
                    enrolled_at=row['enrolled_at']
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded courses and materials'))
