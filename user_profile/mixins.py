from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from post.utils import email_verification

User = get_user_model()


class CleanUserDetailsMixin:
    """A mixin to clean the fields used for user registration"""

    def clean_username(self):
        """Return username in lower case"""
        return self.cleaned_data.get('username').lower()

    def clean_email(self):
        """
        Returns
            email address in lower case if email is unique
            error message in case it isn't.
        """
        email = self.cleaned_data.get('email').lower()
        if not email_verification(email):
            raise forms.ValidationError(
                _('Are you sure %(email)s is a valid email address? We suspect you made a typing error'),
                code='invalid',
                params={'email': email})

        username = self.cleaned_data.get('username').lower()
        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError(
                _('%(email)s is already associated with another account.'),
                code='invalid',
                params={'email': email})
        return email

    def clean_first_name(self):
        """Verify whether the input is a valid alphabetic"""
        first_name = self.cleaned_data.get('first_name')
        # replace spaces as spaces aren't considered alphabetic by isalpha
        if not first_name.replace(' ', '').isalpha():
            raise forms.ValidationError(
                _('Are you sure that %(first_name)s a valid name. Names can only have alphabets'),
                code='invalid',
                params={'first_name': first_name})
        return first_name.strip()

    def clean_last_name(self):
        """Verify whether the input is alphabetic when there's one"""
        last_name = self.cleaned_data.get('last_name')
        if last_name and not last_name.isalpha():
            raise forms.ValidationError(
                _('Are you sure that %(last_name)s a valid name. Names can only have alphabets'),
                code='invalid',
                params={'last_name': last_name})
        return last_name.strip()
