# Generated by Django 2.2.5 on 2019-09-13 21:21

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0013_auto_20190913_1850'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='join_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
