# Generated by Django 2.2.5 on 2019-11-23 16:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0016_profile_test_cols'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='test_cols',
        ),
    ]