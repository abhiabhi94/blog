from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'password1', 'password2']

    def clean_username(self):
        '''Return username in lower case'''
        return self.cleaned_data.get('username').lower()

    def clean_email(self):
        '''
        Returns
            email address in lower case if email is unique
            error message in case it isn't.
        '''
        email = self.cleaned_data.get('email').lower()
        username = self.cleaned_data.get('username').lower()
        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError(
                f'This email address is already associated with another account.')
        return email


class UserUpdateForm(forms.ModelForm):
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
