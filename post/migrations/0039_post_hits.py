# Generated by Django 2.2.5 on 2019-12-15 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0038_auto_20191215_1112'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='hits',
            field=models.PositiveIntegerField(default=0),
        ),
    ]