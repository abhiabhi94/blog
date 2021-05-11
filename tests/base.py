import os
import random
import sys
from string import ascii_lowercase
from typing import Any

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from Blog.models import Category, Post
from blog.settings import BASE_DIR

User = get_user_model()
TEST_DATABASE = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


@override_settings(DATABASES=TEST_DATABASE)
class TestBase(TestCase):
    maxDiff = None

    def get_unique_email(self) -> str:
        """
        Get a valid email

        Returns:
            str
        """
        email = self.get_email()
        email_username, domain = email.split('@')
        # this will only work for Gmail, not tested for other domains
        letters = ascii_lowercase
        random_string = ''.join(random.choice(letters) for i in range(5))
        return f'{email_username}+{random_string}@{domain}'

    def setUp(self):
        """Set the environment variable to disable RECAPTCHA"""
        super().setUp()
        os.environ['RECAPTCHA_DISABLE'] = 'True'

    @staticmethod
    def get_email() -> str:
        """
        Get email set as an environment variable

        Returns:
            str
        """
        variable = 'VALID_EMAIL'
        email = os.getenv(variable)
        if not email:
            sys.exit(
                f'Please set an environment variable {variable} as a valid email. It will be used for testing.')
        return email.strip().lower()

    @classmethod
    def setUpClass(cls) -> None:
        """Initialize all global testing data here."""
        super().setUpClass()
        cls.email = cls.get_email()
        cls.user_data = {
            'username': 'tester',
            'email': cls.email,
            'password': 'user123#',
            'first_name': 'Jach',
            'last_name': 'Karta'
        }
        cls.user = cls.create_user(**cls.user_data)
        cls.user_1_data = cls.user_data.copy()
        cls.user_1_data.update(
            {'username': 'tester_1', 'email': 'a@a.com'})
        cls.user_1 = cls.create_user(**cls.user_1_data)
        cls.posts = 0
        cls.categories = 0

    @classmethod
    def create_user(cls, *args, **kwargs) -> User:
        return User.objects.create(*args, **kwargs)

    @classmethod
    def create_post(cls, title: str, tags: str, *args, **kwargs) -> Post:
        post = Post.objects.create(
            title=title,
            tags=tags,
            author=cls.user,
            *args, **kwargs,
        )
        cls.posts += 1
        return post

    @classmethod
    def create_category(cls, name: str) -> Category:
        category = Category.objects.create(name=name)
        cls.categories += 1
        return category

    def assertQuerysetEqual(self, qs, values, transform=None, *args, **kwargs):
        attr = 'transform'
        if (not transform) and (not kwargs.get(attr, None)) and (transform not in args):
            kwargs.pop(attr, None)
            if attr in args:
                args.remove(attr)
        return super().assertQuerysetEqual(qs, values, transform=lambda x: x, *args, **kwargs)


class TestBaseView(TestBase):
    def setUp(self) -> None:
        """Log in the user"""
        super().setUp()
        self.client.force_login(self.user)


class TestAJAXView(TestBaseView):
    def request(self, url: str, method: str = 'post', is_ajax: bool = True, *args, **kwargs) -> Any:
        """
        A utility function to return performed client requests.
        Args:
            url (str): The url to perform that needs to be requested.
            method (str, optional): The HTTP method name. Defaults to 'POST'.
            is_ajax (bool, optional): Whether AJAX request is to be performed or not. Defaults to True.
        Raises:
            ValueError: When a invalid HTTP method name is passed.
        Returns:
            `Any`: Response from the request.
        """
        request_method = getattr(self.client, method.lower(), None)
        if not request_method:
            raise ValueError('This is not a valid request method')
        if is_ajax:
            return request_method(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest', *args, **kwargs)
        return request_method(url, *args, **kwargs)
