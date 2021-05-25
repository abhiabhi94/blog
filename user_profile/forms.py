from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from user_profile.mixins import CleanUserDetailsMixin
from user_profile.models import Profile

User = get_user_model()


class UserRegistrationForm(UserCreationForm, CleanUserDetailsMixin):
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


class UserUpdationForm(forms.ModelForm, CleanUserDetailsMixin):
    """Allows users to update their personal information"""
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class ProfileUpdationForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['public', 'bio', 'image', 'website', 'location',
                  #   'facebook',
                  'twitter', 'instagram', 'linkedin']
