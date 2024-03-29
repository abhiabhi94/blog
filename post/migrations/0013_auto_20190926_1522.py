# Generated by Django 2.2.5 on 2019-09-26 15:22

from django.db import migrations
import django_markup.fields


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0012_auto_20190926_0847'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='_content_rendered',
        ),
        migrations.RemoveField(
            model_name='post',
            name='_short_des_rendered',
        ),
        migrations.RemoveField(
            model_name='post',
            name='content_markup_type',
        ),
        migrations.RemoveField(
            model_name='post',
            name='short_des_markup_type',
        ),
        migrations.AlterField(
            model_name='post',
            name='content',
            field=django_markup.fields.MarkupField(choices=[('none', 'None (no processing)'), ('linebreaks', 'Linebreaks'), ('markdown', 'Markdown'), ('restructuredtext', 'reStructuredText')], default='markdown', help_text='This field supports all markup formatting', max_length=255, verbose_name='markup'),
        ),
        migrations.AlterField(
            model_name='post',
            name='short_des',
            field=django_markup.fields.MarkupField(blank=True, choices=[('none', 'None (no processing)'), ('linebreaks', 'Linebreaks'), ('markdown', 'Markdown'), ('restructuredtext', 'reStructuredText')], default='markdown', help_text='This will be displayed on the home page.If you leave it blank, the first 50 words from your article will be displayed.It can not be more than 50 words', max_length=500, verbose_name='markup'),
        ),
    ]
