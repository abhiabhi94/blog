# Generated by Django 2.2.5 on 2019-09-13 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0010_auto_20190913_1834'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='website',
            field=models.URLField(blank=True, null=True),
        ),
    ]