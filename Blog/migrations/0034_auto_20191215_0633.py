# Generated by Django 2.2.5 on 2019-12-15 01:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Blog', '0033_post_thumbnail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='thumbnail',
            field=models.ImageField(blank=True, editable=False, null=True, upload_to=''),
        ),
    ]
