# Generated by Django 2.2.5 on 2019-12-15 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Blog', '0037_auto_20191215_1109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='thumbnail',
            field=models.ImageField(blank=True, default='default.jpg', upload_to=''),
        ),
    ]
