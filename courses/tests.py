from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import *
from users.models import User
from .forms import *
from datetime import date
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.contrib.auth.models import Group, Permission

User = get_user_model()

# --------------------------- MODELS TESTS -------------------------------

class CourseModelTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='teacher',
            password='testpassword',
            real_name='Teacher User',
            user_type='teacher'
        )
        self.course = Course.objects.create(
            name='Test Course',
            description='A course for testing',
            teacher=self.teacher,
            deadline=date.today()
        )

    def test_course_creation(self):
        """Test that a course can be created successfully"""
        self.assertEqual(self.course.name, 'Test Course')
        self.assertEqual(self.course.description, 'A course for testing')
        self.assertEqual(self.course.teacher, self.teacher)
        self.assertEqual(self.course.deadline, date.today())

    def test_course_str(self):
        """Test the string representation of the course model."""
        self.assertEqual(str(self.course), 'Test Course')

class CourseMaterialModelTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='teacher',
            password='testpassword',
            real_name='Teacher User',
            user_type='teacher'
        )
        self.course = Course.objects.create(
            name='Test Course',
            description='A course for testing',
            teacher=self.teacher,
            deadline=date.today()
        )
        self.material = CourseMaterial.objects.create(
            course=self.course,
            title='Test Material',
            file='path/to/file.pdf'
        )

    def test_material_creation(self):
        """Test that course material can be uploaded successfully."""
        self.assertEqual(self.material.course, self.course)
        self.assertEqual(self.material.title, 'Test Material')
        self.assertEqual(self.material.file, 'path/to/file.pdf')

    def test_material_str(self):
        """Test the string representation of the course material model."""
        expected_str = f"Material for {self.course.name} uploaded at {self.material.uploaded_at}"
        self.assertEqual(str(self.material), expected_str)

class FeedbackModelTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='student',
            password='testpassword',
            real_name='Student User',
            user_type='student'
        )
        self.course = Course.objects.create(
            name='Test Course',
            description='A course for testing',
            teacher=self.student
        )
        self.feedback = Feedback.objects.create(
            course=self.course,
            student=self.student,
            comment='Great course!'
        )

    def test_feedback_creation(self):
        """Test a course feedback can be created successfully."""
        self.assertEqual(self.feedback.course, self.course)
        self.assertEqual(self.feedback.student, self.student)
        self.assertEqual(self.feedback.comment, 'Great course!')

    def test_feedback_str(self):
        """Test the string representation of the course feedback model."""
        expected_str = f'Feedback by {self.student} on {self.course}'
        self.assertEqual(str(self.feedback), expected_str)

class EnrollmentModelTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='student',
            password='testpassword',
            real_name='Student User',
            user_type='student'
        )
        self.course = Course.objects.create(
            name='Test Course',
            description='A course for testing',
            teacher=self.student
        )
        self.enrollment = Enrollment.objects.create(
            course=self.course,
            student=self.student,
            is_blocked=False
        )

    def test_enrollment_creation(self):
        """Test a course enrollment can be created successfully."""
        self.assertEqual(self.enrollment.course, self.course)
        self.assertEqual(self.enrollment.student, self.student)
        self.assertFalse(self.enrollment.is_blocked)

    def test_enrollment_str(self):
        """Test the string representation of the enrollment model."""
        expected_str = f'{self.student} enrolled in {self.course}'
        self.assertEqual(str(self.enrollment), expected_str)

# --------------------------- FORMS TESTS -------------------------------

class CourseFormTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='teacher',
            password='testpassword',
            real_name='Teacher User',
            user_type='teacher'
        )

    def test_course_form_valid_data(self):
        """Test that a valid form creates a course correctly."""
        form_data = {
            'name': 'Test Course',
            'description': 'This is a test course',
            'deadline': date.today(),
        }
        form = CourseForm(data=form_data)
        self.assertTrue(form.is_valid())
        course = form.save(commit=False)
        course.teacher = self.teacher
        course.save()
        self.assertEqual(course.name, 'Test Course')
        self.assertEqual(course.description, 'This is a test course')
        self.assertEqual(course.deadline, date.today())

    def test_course_form_invalid_data(self):
        """Test that an invalid form fails."""
        form_data = {
            'name': '',  # Invalid: name is required
            'description': 'This is a test course',
        }
        form = CourseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

class CourseMaterialFormTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='teacher',
            password='testpassword',
            real_name='Teacher User',
            user_type='teacher'
        )
        self.course = Course.objects.create(
            name='Test Course',
            description='This is a test course',
            teacher=self.teacher
        )

    def test_material_form_valid_data(self):
        """Test that a valid form uploads course material correctly."""
        form_data = {
            'title': 'Test Material',
        }
        file = SimpleUploadedFile(name='test_file.pdf', content=b'file_content', content_type='application/pdf')
        form = CourseMaterialForm(data=form_data, files={'file': file})
        self.assertTrue(form.is_valid())
        material = form.save(commit=False)
        material.course = self.course
        material.save()
        self.assertEqual(material.title, 'Test Material')
        # Reopen the file to verify its content
        self.assertEqual(material.file.read(), b'file_content')

    def test_material_form_invalid_data(self):
        """Test that an invalid form fails."""
        form_data = {
            'title': '',  # Invalid: title is required
        }
        form = CourseMaterialForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

class FeedbackFormTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='student',
            password='testpassword',
            real_name='Student User',
            user_type='student'
        )
        self.course = Course.objects.create(
            name='Test Course',
            description='This is a test course',
            teacher=self.student
        )

    def test_feedback_form_valid_data(self):
        """Test that a valid form creates a course feedback correctly."""
        form_data = {
            'course': self.course.id,
            'comment': 'Great course!'
        }
        form = FeedbackForm(data=form_data)
        self.assertTrue(form.is_valid())
        feedback = form.save(commit=False)
        feedback.student = self.student
        feedback.save()
        self.assertEqual(feedback.comment, 'Great course!')
        self.assertEqual(feedback.course, self.course)

    def test_feedback_form_invalid_data(self):
        """Test that an invalid form fails."""
        form_data = {
            'course': self.course.id,
            'comment': '',  # Invalid: comment is required
        }
        form = FeedbackForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('comment', form.errors)

# --------------------------- VIEWS TESTS -------------------------------

class CoursesViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='teacher',
            password='testpassword',
            real_name='Teacher User',
            user_type='teacher'
        )
        # Create the 'Teachers' group
        teachers_group = Group.objects.create(name='Teachers')
        # Add the 'can_manage_courses' permission to the 'Teachers' group
        can_manage_courses = Permission.objects.get(codename='can_manage_courses')
        teachers_group.permissions.add(can_manage_courses)
        # Assign the teacher to the 'Teachers' group
        self.teacher.groups.add(teachers_group)

        self.student = User.objects.create_user(
            username='student',
            real_name='Test Student',
            password='testpassword',
            user_type='student'
        )
        self.course = Course.objects.create(
            name='Test Course',
            description='Course Description',
            teacher=self.teacher,
            deadline='2024-12-31'
        )
        self.enrollment = Enrollment.objects.create(
            course=self.course,
            student=self.student,
            is_blocked=False
        )
    
    def test_course_detail_view(self):
        self.client.login(username='student', password='testpassword')
        response = self.client.get(reverse('course_detail', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course_detail.html')
        self.assertEqual(response.context['course'], self.course)

    def test_create_course_view(self):
        can_manage_courses = Permission.objects.get(codename='can_manage_courses')
        self.teacher.user_permissions.add(can_manage_courses)
        self.client.login(username='teacher', password='testpassword')
        response = self.client.post(reverse('create_course'), {
            'name': 'New Course',
            'description': 'New Course Description',
            'deadline': '2024-12-31'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after creation
        self.assertTrue(Course.objects.filter(name='New Course').exists())

    def test_enroll_in_course(self):
        self.client.login(username='student', password='testpassword')
        response = self.client.post(reverse('enroll_in_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)  # Should redirect after enrollment
        self.assertTrue(Enrollment.objects.filter(course=self.course, student=self.student).exists())

    def test_leave_feedback_view(self):
        self.client.login(username='student', password='testpassword')
        response = self.client.post(reverse('leave_feedback', args=[self.course.id]), {
            'comment': 'Great course!',
            'course': self.course.id
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after feedback submission
        self.assertTrue(Feedback.objects.filter(course=self.course, student=self.student, comment='Great course!').exists())

    def test_upload_material_view(self):
        can_manage_courses = Permission.objects.get(codename='can_manage_courses')
        self.teacher.user_permissions.add(can_manage_courses)
        self.client.login(username='teacher', password='testpassword')
        # Create a test file
        test_file = SimpleUploadedFile("testfile.txt", b"Test file content", content_type="text/plain")
        response = self.client.post(reverse('upload_material', args=[self.course.id]), {
            'title': 'New Material',
            'file': test_file
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after material upload
        # Check if the material was uploaded
        self.assertTrue(CourseMaterial.objects.filter(course=self.course, title='New Material').exists())

    def test_remove_student_view(self):
        # Add permission specifically for this test case
        can_manage_courses = Permission.objects.get(codename='can_manage_courses')
        self.teacher.user_permissions.add(can_manage_courses)

        self.client.login(username='teacher', password='testpassword')
        response = self.client.post(reverse('remove_student', args=[self.course.id, self.student.id]))
        self.assertEqual(response.status_code, 302)  # Should redirect after removing
        self.assertFalse(Enrollment.objects.filter(course=self.course, student=self.student).exists())

    def test_block_student_view(self):
        # Add permission specifically for this test case
        can_manage_courses = Permission.objects.get(codename='can_manage_courses')
        self.teacher.user_permissions.add(can_manage_courses)
        
        self.client.login(username='teacher', password='testpassword')
        response = self.client.post(reverse('block_student', args=[self.course.id, self.student.id]))
        self.assertEqual(response.status_code, 302)  # Should redirect after blocking
        enrollment = Enrollment.objects.get(course=self.course, student=self.student)
        self.assertTrue(enrollment.is_blocked)  # Student should be blocked

    def test_unblock_student_view(self):
        # Add permission specifically for this test case
        can_manage_courses = Permission.objects.get(codename='can_manage_courses')
        self.teacher.user_permissions.add(can_manage_courses)
        
        self.client.login(username='teacher', password='testpassword')
        response = self.client.post(reverse('unblock_student', args=[self.course.id, self.student.id]))
        self.assertEqual(response.status_code, 302)  # Should redirect after unblocking
        enrollment = Enrollment.objects.get(course=self.course, student=self.student)
        self.assertFalse(enrollment.is_blocked)  # Student should be blocked