# Generated by Django 2.2.5 on 2019-12-22 18:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0040_auto_20191216_0455'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='hits',
        ),
    ]
