from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, reverse
from django.test import TestCase

from post.models import Category
from post.views import HomeView
from user_profile.forms import UserRegistrationForm


class UserDetailsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Initialise the form data"""
        user_data = {
            'username': 'Tester',
            'first_name': 'Jach',
            'email': 'Jachkarta@gmail.com',
            'password1': 'user123#',
            'password2': 'user123#',
        }
        # create a user for testing purpose
        form = UserRegistrationForm(user_data)
        form.save()
        # Create a superuser
        super_user = User.objects.create_superuser(username='superuser',
                                                   email='a@a.com',
                                                   password='123'
                                                   )
        # Current home page requires these categories
        for category in HomeView.HOME_CATEGORIES:
            Category.objects.create(name=category,
                                    info='Testing category',
                                    author=super_user
                                    )

    def test_correct_template_used_for_register(self):
        """
        Test if correct template is used for the register url
        """
        # Testing register
        register = self.client.get(reverse('register'))
        # Test HTTP response
        self.assertEqual(register.status_code, 200)
        self.assertTemplateUsed(
            register, template_name='user_profile/register.html')

    def test_username_case_insensitive(self):
        """Test whether username field is case insensitive"""
        email = 'jachkarta@gmail.com'
        username = 'tester'

        user = User.objects.get(email=email)
        self.assertEqual(user.username, username)

    def test_email_case_insensitive(self):
        """Test whether email field is case insensitive"""
        email = 'jachkarta@gmail.com'
        username = 'tester'

        user = User.objects.get(username=username)
        self.assertEqual(user.email, email)

    def test_email_integrity(self):
        """
        Test invalidation for use of 1 email by more than 1 accounts,\
            raising of appropriate validation error
        """
        email = 'jachkarta@gmail.com'

        form = UserRegistrationForm(data={'email': email, 'username': 'test'})
        # Test invalidation of form
        self.assertFalse(form.is_valid())
        # Test if validation error is raised
        self.assertEqual(form.has_error('email', code='invalid'), True)

    def test_redirect_on_successful_registration(self):
        """Test redirect to home page on successful registration"""
        data = {
            'username': 'tester1',
            'first_name': 'Jach',
            'email': 'jachkarta+test@gmail.com',
            'password1': 'user123#',
            'password2': 'user123#',
        }
        response = self.client.post(reverse('register'), data=data)
        self.assertRedirects(response, expected_url=reverse('post:home'))

    def test_redirect_authenticated_user_on_register(self):
        """Test whether a logged in user is redirected to home when trying to access register link"""
        self.client.login(username='tester', password='user123#')
        response = self.client.get(reverse('register'))
        self.assertRedirects(response, expected_url=reverse('post:home'))

    def test_redirect_unauthenticated_user_on_profile(self):
        """Test whether a logged in user is redirected to home when trying to access register link"""
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, expected_url='/login/?next=/profile/')

    def test_profile_updation(self):
        """
        TODO:
            This test is not comphrensive, many fields are yet to be tested

        Test whether
            - profile urls loads successfully
            - correct template is used for rendering
            - data is updated successfully on post request
        """
        new_data = {
            'username': 'tester2',
            'first_name': 'Jachi',
            'last_name': 'karta',
            'email': 'jachkarta+test1@gmail.com',
        }
        url_profile = reverse('profile')
        self.client.login(username='tester', password='user123#')
        # Test GET request
        profile_get = self.client.get(url_profile)
        self.assertEqual(profile_get.status_code, 200)
        self.assertTemplateUsed(
            profile_get, template_name='user_profile/profile.html')

        # Test POST request
        profile_post = self.client.post(url_profile, data=new_data)
        # Test HTTP response
        self.assertEqual(profile_post.status_code, 200)

        user = get_object_or_404(User, username=new_data['username'])

        # Test profile values
        self.assertEqual(user.username, new_data['username'])
        self.assertEqual(user.first_name, new_data['first_name'])
        self.assertEqual(user.last_name, new_data['last_name'])
        self.assertEqual(user.email, new_data['email'])

    def test_password_change(self):
        """Test whether users can change their password and are logged back in"""
        username = 'tester'
        data = {
            'old_password': 'user123#',
            'new_password1': 'NewUser123#',
            'new_password2': 'NewUser123#'
        }
        url = reverse('password-change')
        self.client.login(username=username, password=data['old_password'])
        password_change = self.client.post(url, data=data)
        self.assertRedirects(
            password_change, expected_url=reverse('post:home'))
