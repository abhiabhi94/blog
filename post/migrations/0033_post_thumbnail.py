# Generated by Django 2.2.5 on 2019-12-15 00:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0032_remove_post_thumbnail'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='thumbnail',
            field=models.ImageField(editable=False, null=True, upload_to=''),
        ),
    ]
