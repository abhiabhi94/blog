from django.test import TestCase

from user_profile.forms import UserRegistrationForm


class UserRegistrationFormTest(TestCase):

    def test_email_invalidates_dummy_emails(self):
        """Test whether email field invalidates dummy emails and raises a validation error"""
        field = 'email'

        form = UserRegistrationForm(data={field: 'ab@ab.com'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.has_error(field, code='invalid'), True)

    def test_first_name_alphabetic(self):
        """Test whether first name invalidates non alphabets and raises a validation error"""
        field = 'first_name'

        form_1 = UserRegistrationForm(data={field: 'Bulb2'})
        self.assertFalse(form_1.is_valid())
        self.assertEqual(form_1.has_error(field, code='invalid'), True)

    def test_first_name_successful(self):
        field = 'first_name'

        form = UserRegistrationForm(data={field: 'a b'})

        self.assertIs(form.has_error(field), False)

    def test_last_name_can_be_blank(self):
        field = 'last_name'

        form = UserRegistrationForm(data={field: ''})

        self.assertIs(form.is_valid(), False)

    def test_last_name_does_not_allow_non_alphabetic_characters(self):
        field = 'last_name'

        form = UserRegistrationForm(data={field: 'Bulb2'})

        self.assertIs(form.is_valid(), False)
        self.assertIs(form.has_error(field, code='invalid'), True)
