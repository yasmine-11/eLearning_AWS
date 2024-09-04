from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from users.models import User, StatusUpdate
from courses.models import Course

class ApiTestBase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create teacher and student users
        self.teacher = User.objects.create_user(username='teacher', password='teacherpass', user_type='teacher')
        self.student = User.objects.create_user(username='student', password='studentpass', user_type='student')

        # Create some StatusUpdates
        self.status1 = StatusUpdate.objects.create(user=self.teacher, content="Teacher's status")
        self.status2 = StatusUpdate.objects.create(user=self.student, content="Student's status")

        # Endpoints
        self.users_url = reverse('user-list')
        self.status_updates_url = reverse('statusupdate-list')

        # Authentication
        self.client.force_authenticate(user=self.teacher)

class UserViewSetTest(ApiTestBase):
    
    def test_teacher_can_view_own_and_students_data(self):
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Teacher should see their own data and student's data

    def test_student_can_only_view_own_data(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Student should only see their own data
        self.assertEqual(response.data[0]['username'], self.student.username)

    def test_teacher_can_update_students_data(self):
        data = {'real_name': 'Updated Student Name'}
        url = reverse('user-detail', args=[self.student.id])
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertEqual(self.student.real_name, 'Updated Student Name')

    def test_student_cannot_update_other_students_or_teachers_data(self):
        data = {'real_name': 'Hacker'}
        url = reverse('user-detail', args=[self.teacher.id])
        self.client.force_authenticate(user=self.student)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.teacher.refresh_from_db()
        self.assertNotEqual(self.teacher.real_name, 'Hacker')

class StatusUpdateViewSetTest(ApiTestBase):

    def test_authenticated_user_can_view_status_updates(self):
        response = self.client.get(self.status_updates_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Teacher can see all statuses

    def test_student_can_create_status_update(self):
        data = {'content': "Student's new status"}
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.status_updates_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(StatusUpdate.objects.filter(content="Student's new status").exists())

    def test_unauthenticated_user_cannot_create_status_update(self):
        self.client.logout()
        data = {'content': "Anonymous status"}
        response = self.client.post(self.status_updates_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_status_update_contains_username(self):
        response = self.client.get(self.status_updates_url)
        self.assertIn('username', response.data[0])
        self.assertEqual(response.data[0]['username'], self.teacher.username)


