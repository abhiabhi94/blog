# Generated by Django 2.2.5 on 2019-12-15 23:25

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Blog', '0039_post_hits'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='_content_rendered',
        ),
        migrations.RemoveField(
            model_name='post',
            name='content_markup_type',
        ),
        migrations.AlterField(
            model_name='post',
            name='content',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
    ]
