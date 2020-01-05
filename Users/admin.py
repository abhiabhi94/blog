from .models import Profile
from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.admin.widgets import FilteredSelectMultiple, ManyToManyRawIdWidget
from django.contrib.auth.models import Group
# from django.contrib.auth.models import User
from Blog.models import Post


User = get_user_model()


# Create ModelForm based on the Group model.
class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = []

    # Add the users field.
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        # Use the pretty 'filter_horizontal widget'.
        # This can cause the site to slowdown or break
        # use ManytoManyRawIdWidget in future
        widget=FilteredSelectMultiple('users', False)
        # widget=ManyToManyRawIdWidget(
        #     User._meta.get_field('username').remote_field, admin.site)
    )

    def __init__(self, *args, **kwargs):
        # Do the normal form initialisation.
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        # If it is an existing group (saved objects have a pk).
        if self.instance.pk:
            # Populate the users field with the current Group users.
            self.fields['users'].initial = self.instance.user_set.all()

    def save_m2m(self):
        # Add the users to the Group.
        self.instance.user_set.set(self.cleaned_data['users'])

    def save(self, *args, **kwargs):
        # Default save
        instance = super(GroupAdminForm, self).save()
        # Save many-to-many data
        self.save_m2m()
        return instance


# Create a new Group admin.
class GroupAdmin(admin.ModelAdmin):
    # Use our custom form.
    form = GroupAdminForm
    # Filter permissions horizontal as well.
    filter_horizontal = ['permissions']


# Unregister the original Group admin.
admin.site.unregister(Group)
# Register the new Group ModelAdmin.
admin.site.register(Group, GroupAdmin)
# Register profile model.
admin.site.register(Profile)
