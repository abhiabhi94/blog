# Generated by Django 2.2.5 on 2019-09-13 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0011_auto_20190913_1839'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='website',
            field=models.EmailField(blank=True, max_length=80, null=True),
        ),
    ]