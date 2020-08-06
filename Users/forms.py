from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm

from Blog.utils import email_verification
from Users.models import Profile


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
                'Are you sure %(email)s is a valid email address? We suspect you made a typing error',
                code='invalid',
                params={'email': email})

        username = self.cleaned_data.get('username').lower()
        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError(
                '%(email)s is already associated with another account.',
                code='invalid',
                params={'email': email})
        return email

    def clean_first_name(self):
        """Verify whether the input is a valid alphabetic"""
        first_name = self.cleaned_data.get('first_name')
        if not first_name.isalpha():
            raise forms.ValidationError(
                'Are you sure that %(first_name)s a valid name. Names can only have alphabets',
                code='invalid',
                params={'first_name': first_name})
        return first_name

    def clean_last_name(self):
        """Verify whether the input is alphabetic when there's one"""
        last_name = self.cleaned_data.get('last_name')
        if last_name and not last_name.isalpha():
            raise forms.ValidationError(
                'Are you sure that %(last_name)s a valid name. Names can only have alphabets',
                code='invalid',
                params={'last_name': last_name})
        return last_name


class UserRegisterForm(UserCreationForm, CleanUserDetailsMixin):
    """
    Register a user by extending the User model with the following information:
        First Name
        Last Name(optional)-> not all people have a last name
        Email
    """
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm, CleanUserDetailsMixin):
    """Allows users to update their personal information"""
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['public', 'bio', 'image', 'website', 'location',
                  #   'facebook',
                  'twitter', 'instagram', 'linkedin']
