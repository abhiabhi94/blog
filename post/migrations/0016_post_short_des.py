# Generated by Django 2.2.5 on 2019-09-26 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0015_auto_20190926_1747'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='short_des',
            field=models.CharField(blank=True, default='', help_text='This will be displayed on the home page.If you leave it blank, the first 50 words from your article will be displayed.It can not be more than 50 words', max_length=500),
        ),
    ]
