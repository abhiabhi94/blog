# Generated by Django 2.2.5 on 2019-09-13 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0007_remove_profile_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='name',
            field=models.CharField(default='New User', max_length=100),
        ),
    ]
