# Generated by Django 2.2.4 on 2019-12-18 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0041_auto_20191218_0137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='info',
            field=models.TextField(help_text='Description of the category.', max_length=5000),
        ),
    ]
