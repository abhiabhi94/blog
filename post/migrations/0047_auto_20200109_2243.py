# Generated by Django 2.2.5 on 2020-01-09 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0046_merge_20200102_0123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(help_text='Name of the category. ex-Coding, Robotics', max_length=50, unique=True),
        ),
    ]