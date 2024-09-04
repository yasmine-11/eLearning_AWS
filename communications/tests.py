from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import *
from .forms import *
from courses.models import Course
from django.urls import reverse

User = get_user_model()

# --------------------------- MODELS TESTS -------------------------------

class CommunicationsModelsTest(TestCase):

    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher', password='teacherpass', user_type='teacher')
        self.student = User.objects.create_user(username='student', password='studentpass', user_type='student')
        self.course = Course.objects.create(name='Test Course', description='Course Description', teacher=self.teacher)

    def test_notification_creation(self):
        notification = Notification.objects.create(
            recipient=self.student,
            sender=self.teacher,
            course=self.course,
            message='New course material uploaded.'
        )
        self.assertEqual(str(notification), f"Notification for {self.student}: {notification.message}")

    def test_chat_message_creation(self):
        chat_message = ChatMessage.objects.create(
            course=self.course,
            user=self.student,
            message='This is a test message.'
        )
        self.assertEqual(str(chat_message), f'{self.student.username}: {chat_message.message[:20]}')

# --------------------------- FORMS TESTS -------------------------------

class CommunicationsFormsTest(TestCase):

    def test_chat_message_form_valid(self):
        form_data = {'message': 'This is a test message.'}
        form = ChatMessageForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_chat_message_form_invalid(self):
        form_data = {}  # Empty form data
        form = ChatMessageForm(data=form_data)
        self.assertFalse(form.is_valid())

# --------------------------- VIEWS TESTS -------------------------------

class CommunicationsViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(username='teacher', password='teacherpass', user_type='teacher')
        self.student = User.objects.create_user(username='student', password='studentpass', user_type='student')
        self.course = Course.objects.create(name='Test Course', description='Course Description', teacher=self.teacher)

    def test_notifications_view(self):
        self.client.login(username='student', password='studentpass')
        Notification.objects.create(recipient=self.student, sender=self.teacher, course=self.course, message='New material uploaded.')
        response = self.client.get(reverse('notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'communications/notifications.html')
        self.assertContains(response, 'New material uploaded.')

    def test_upload_chat_file_view(self):
        self.client.login(username='teacher', password='teacherpass')
        with open('testfile.txt', 'w') as f:
            f.write("Test file content")

        with open('testfile.txt', 'rb') as f:
            response = self.client.post(reverse('upload_chat_file', args=[self.course.id]), {
                'message': 'Check this file',
                'file': f
            })
        
        self.assertEqual(response.status_code, 302)  # Should redirect after upload
        self.assertTrue(ChatMessage.objects.filter(course=self.course, user=self.teacher, message='Check this file').exists())