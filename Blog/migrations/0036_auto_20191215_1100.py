# Generated by Django 2.2.5 on 2019-12-15 05:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Blog', '0035_auto_20191215_1058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='thumbnail',
            field=models.ImageField(default='default.jpg', editable=False, upload_to=''),
        ),
    ]
