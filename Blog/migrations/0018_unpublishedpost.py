# Generated by Django 2.2.5 on 2019-09-27 07:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Blog', '0017_remove_post_short_des'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnPublishedPost',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='Blog.Post')),
            ],
            bases=('Blog.post',),
        ),
    ]
