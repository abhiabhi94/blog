# Generated by Django 2.2.4 on 2019-12-17 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0040_auto_20191216_0455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='info',
            field=models.TextField(help_text='Description of the category.', max_length=5000),
        ),
    ]
