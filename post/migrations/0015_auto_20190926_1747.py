# Generated by Django 2.2.5 on 2019-09-26 17:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0014_auto_20190926_1628'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='_short_des_rendered',
        ),
        migrations.RemoveField(
            model_name='post',
            name='short_des',
        ),
        migrations.RemoveField(
            model_name='post',
            name='short_des_markup_type',
        ),
    ]
