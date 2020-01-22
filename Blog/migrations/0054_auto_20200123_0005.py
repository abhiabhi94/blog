# Generated by Django 2.2.5 on 2020-01-22 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Blog', '0053_auto_20200121_2115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='state',
            field=models.SmallIntegerField(choices=[(-1, 'Draft'), (0, 'Queued'), (1, 'Published')], default=-1),
        ),
    ]
