from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import *
from .forms import *
from .views import *
from django.urls import reverse
from django.contrib.auth.models import Group


# --------------------------- MODELS TESTS -------------------------------

class UserModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            real_name='Test User',
            password='testpassword',
            user_type='student'
        )

    def test_user_creation(self):
        """Test that a user can be created successfully."""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.real_name, 'Test User')
        self.assertEqual(self.user.user_type, 'student')

    def test_user_str_method(self):
        """Test the string representation of the User model."""
        self.assertEqual(str(self.user), 'testuser')

    def test_user_type_choices(self):
        """Test that user_type choices work correctly."""
        self.assertEqual(self.user.user_type, 'student')
        self.user.user_type = 'teacher'
        self.user.save()
        self.assertEqual(self.user.user_type, 'teacher')

    def test_optional_photo_field(self):
        """Test that the photo field can be blank."""
        self.assertIsNone(self.user.photo.name)


class StatusUpdateModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            real_name='Test User',
            password='testpassword',
            user_type='student'
        )
        self.status_update = StatusUpdate.objects.create(
            user=self.user,
            content="This is a test status update."
        )

    def test_status_update_creation(self):
        """Test that a status update can be created successfully."""
        self.assertEqual(self.status_update.user, self.user)
        self.assertEqual(self.status_update.content, "This is a test status update.")

    def test_status_update_str_method(self):
        """Test the string representation of the StatusUpdate model."""
        expected_str = f"{self.user.username} - {self.status_update.created_at} - This is a test status update."
        self.assertEqual(str(self.status_update)[:50], expected_str[:50])

    def test_status_update_auto_now_add(self):
        """Test that created_at is automatically populated."""
        self.assertIsNotNone(self.status_update.created_at)

# --------------------------- FORMS TESTS -------------------------------

class UserRegistrationFormTest(TestCase):

    def test_valid_user_registration_form(self):
        """Test that a valid form registers a user correctly."""
        form_data = {
            'username': 'testuser',
            'real_name': 'Test User',
            'user_type': 'student',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.real_name, 'Test User')
        self.assertEqual(user.user_type, 'student')

    def test_invalid_user_registration_form(self):
        """Test that an invalid form fails."""
        form_data = {
            'username': 'testuser',
            'real_name': 'Test User',
            'user_type': 'student',
            'password1': 'strongpassword123',
            'password2': 'differentpassword',  # Passwords don't match
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_missing_required_fields(self):
        """Test that required fields are enforced."""
        form_data = {
            'username': 'testuser',
            # Missing 'real_name'
            'user_type': 'student',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('real_name', form.errors)

class StatusUpdateFormTest(TestCase):

    def test_valid_status_update_form(self):
        """Test that a valid form saves a status update correctly."""
        form_data = {
            'content': 'This is a test status update.',
        }
        form = StatusUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())
        status_update = form.save(commit=False)
        # Add user before saving
        status_update.user = User.objects.create_user(
            username='testuser',
            real_name='Test User',
            password='testpassword',
            user_type='student'
        )
        status_update.save()
        self.assertEqual(status_update.content, 'This is a test status update.')

    def test_invalid_status_update_form(self):
        """Test that an invalid form fails."""
        form_data = {
            'content': '',  # Content is required
        }
        form = StatusUpdateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

# --------------------------- VIEWS TESTS -------------------------------

class UserRegistrationViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        # Create groups that users will be assigned to
        Group.objects.create(name='Teachers')
        Group.objects.create(name='Students')

    def test_register_valid_data(self):
        """Tests registering with valid data."""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'real_name': 'New User',
            'user_type': 'student',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after registration
        user = User.objects.get(username='newuser')
        self.assertEqual(user.real_name, 'New User')
        self.assertEqual(user.user_type, 'student')
        self.assertTrue(user.is_authenticated)
        self.assertTrue(user.groups.filter(name='Students').exists())

    def test_register_invalid_data(self):
        """Tests registering with invalid data."""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'real_name': 'New User',
            'user_type': 'student',
            'password1': 'strongpassword123',
            'password2': 'differentpassword'  # Passwords don't match
        })
        self.assertEqual(response.status_code, 200)  # Should stay on the same page
        self.assertFormError(response, 'form', 'password2', "The two password fields didn’t match.")
        self.assertFalse(User.objects.filter(username='newuser').exists())  # User should not be created

class UserLoginViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )

    def test_login_valid(self):
        """Test a valid login."""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after login
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_invalid(self):
        """Test an invalid login."""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Should stay on the same page
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertFormError(response, 'form', None, 'Please enter a correct username and password. Note that both fields may be case-sensitive.')

class HomeViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='teacher',
            password='testpassword',
            user_type='teacher'
        )
        self.student = User.objects.create_user(
            username='student',
            password='testpassword',
            user_type='student'
        )

    def test_teacher_home(self):
        """Test teacher home can be correctly accessed."""
        self.client.login(username='teacher', password='testpassword')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/teacher_home.html')

    def test_student_home(self):
        """Test student home can be correctly accessed."""
        self.client.login(username='student', password='testpassword')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/student_home.html')

class UserProfileViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            user_type='student'
        )

    def test_user_profile(self):
        """Test user profile can be correctly accessed."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('user_profile', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/user_profile.html')
        self.assertEqual(response.context['profile_user'], self.user)

class StatusUpdateViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            user_type='student'
        )

    def test_status_update_valid(self):
        """Test a valid status update upload."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('status_update'), {
            'content': 'This is a test status update.'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after submission
        self.assertTrue(StatusUpdate.objects.filter(user=self.user, content='This is a test status update.').exists())

    def test_status_update_invalid(self):
        """Test an invalid status update upload."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('status_update'), {
            'content': ''  # Invalid because content is required
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(StatusUpdate.objects.filter(user=self.user).exists())  # Should not save the update
        self.assertFormError(response, 'form', 'content', 'This field is required.')

class SearchProfilesViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='student',
            password='testpassword',
            real_name='Student User',
            user_type='student'
        )
        self.teacher = User.objects.create_user(
            username='teacher',
            password='testpassword',
            real_name='Teacher User',
            user_type='teacher'
        )

    def test_search_profiles_as_student(self):
        """Test search functionality as a student"""
        self.client.login(username='student', password='testpassword')
        response = self.client.get(reverse('search_profiles'), {'q': 'Student'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.student, response.context['results'])
        self.assertNotIn(self.teacher, response.context['results'])

    def test_search_profiles_as_teacher(self):
        """Test search functionality as a teacher"""
        self.client.login(username='teacher', password='testpassword')
        response = self.client.get(reverse('search_profiles'), {'q': 'User'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.student, response.context['results'])
        self.assertIn(self.teacher, response.context['results'])



