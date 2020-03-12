from django.test import TestCase
from Users.forms import UserRegisterForm, UserUpdateForm


class UserRegistrationFormTest(TestCase):

    def test_email_invalidates_dummy_emails(self):
        """Test whether email field invalidates dummy emails and raises a validation error"""
        field = 'email'

        form = UserRegisterForm(data={field: 'ab@ab.com'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.has_error(field, code='invalid'), True)

    def test_first_name_alphabetic(self):
        """Test whether first name invalidates non alphabets and raises a validation error"""
        field = 'first_name'

        form_1 = UserRegisterForm(data={field: 'Bulb2'})
        self.assertFalse(form_1.is_valid())
        self.assertEqual(form_1.has_error(field, code='invalid'), True)

        form_2 = UserRegisterForm(data={field: '$Bulb_'})
        self.assertFalse(form_2.is_valid())
        self.assertEqual(form_2.has_error(field, code='invalid'), True)

    def test_last_name_alphabetic(self):
        """
        Test whether last name either accepts
            - accepts blank value
            - invalidates non alphabet values
                raises a validation error if it fails
        """
        field = 'last_name'

        form_1 = UserRegisterForm(data={field: ''})
        self.assertFalse(form_1.is_valid())

        form_2 = UserRegisterForm(data={field: 'Bulb2'})
        self.assertFalse(form_2.is_valid())
        self.assertEqual(form_2.has_error(field, code='invalid'), True)

        form_3 = UserRegisterForm(data={field: '$Bulb_'})
        self.assertFalse(form_3.is_valid())
        self.assertEqual(form_3.has_error(field, code='invalid'), True)
