import re
import os
from django.utils.html import strip_tags
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.template.defaultfilters import slugify
from markupfield.fields import MarkupField
from Track.models import UrlHit
from meta.models import ModelMeta
from PIL import Image
from django.core.files import File
from io import BytesIO
from django.core.files.base import ContentFile

# from django.contrib.messages import messages


class Category(models.Model, ModelMeta):
    name = models.CharField(help_text=(
        "Name of the category. ex-Science, Technology"), max_length=50, unique=True)
    info = models.TextField(help_text=(
        "Description of the category."), max_length=5000, unique=True)
    date_created = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    # author of this category.
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    _metadata = {
        'Category': 'name',
        'Info': 'info'
    }

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super(*args, **kwargs).save()

    def __str__(self):
        '''helps in showing name in foreign key field instead of category object'''
        return self.name


class Post(models.Model, ModelMeta):
    title = models.CharField(
        help_text='Try to keep the title short, within 80 characters.', max_length=80, unique=True)
    slug = models.SlugField(default='', max_length=80)
    # short_des = models.CharField(help_text=('This will be displayed on the home page.'
    #                                 'If you leave it blank, the first 50 words from your article will be displayed.'
    #                                 'It can not be more than 50 words'),
    #                             default='',
    #                             max_length=500,
    #                             blank=True,
    #                         # default_markup_type='markdown',
    #                         )
    # content = models.TextField()
    content = MarkupField(help_text=('This field supports all markup formatting'),
                          default='',
                          default_markup_type='markdown',
                          )
    tags = models.CharField(
        help_text='Enter tags separated by spaces. Do not enter more than 5 tags', max_length=80, default='', blank=True)
    date_posted = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(
        Category, null=True, on_delete=models.SET_NULL)
    publish = models.BooleanField(default=False)
    date_published = models.DateTimeField(
        null=True, blank=True)
    featured = models.BooleanField(default=False)
    image = models.ImageField(
        default='default.jpg', upload_to='blog', blank=True)
    thumbnail = models.ImageField(editable=False, null=True, blank=True)
    _metadata = {
        'title': 'title',
        'description': 'get_short_des',
        'keywords': 'get_tags_list',
    }

    def save(self, *args, **kwargs):
        '''
        1. slugify the title
        2. save the tags in lower case
        3. Sets the date_publish when the publish flag is set for the first time.
        4. compress and resize images to make thumbnails and full size images
        '''

        super(*args, **kwargs).save()

        self.slug = slugify(self.title)
        self.tags = self.tags.lower()

        # Save the publish date when the flag is set for the first time.
        if self.publish and self.date_published is None:
            self.date_published = timezone.now()

        with Image.open(self.image.path) as img:
            thumbnail_size, full_view_size = (350, 350), (800, 800)

            img_thumbnail = img.copy()  # thumbnail changes in place

            # for list and card view
            img_thumbnail.thumbnail(thumbnail_size)
            thumbnail_name = self._image_name('_thumbnail')
            img_thumbnail.save(thumbnail_name, quality=50, optimize=True)

            with open(self.image.path, 'rb') as f:
                data = f.read()

            # print(BytesIO(data), '\n')
            # print('file>>>', File(f))
            self.thumbnail.save(thumbnail_name, File(f))
            # for detail view
            img.thumbnail(full_view_size)
            img.save(self.image.path, quality=50, optimize=True)
        # Remove the original image
        # os.remove(self.image.path)

    @property
    def full_view_image(self):
        '''To be used in template for getting the url of full_view_image for detail view'''

        return self._image_name('_full_view', True)

    @property
    def thumbnail_image(self):
        '''To be used in template for getting the url of full_view_image for list view'''

        # self.image.path = self._image_name('_thumbnail', True)

        return self._image_name('_thumbnail', True)

    def _image_name(self, modifier, view=False):
        '''
        modifier - used for changing the name for image
        view - if true return url for template else return path for saving.
        '''
        new_name = self.image.name.split('.')
        new_name.insert(-1, modifier+'.')  # dont forget extension
        if view:
            return self.image.storage.url(''.join(new_name))
        return self.image.storage.path(''.join(new_name))

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('Blog:post-preview', kwargs={
            'year': self.date_posted.year,
            'month': self.date_posted.month,
            'day': self.date_posted.day,
            'slug': self.slug
        })

    def get_short_des(self):
        # Remove html tags and continuous whitespaces
        text_only = re.sub('[ \t]+', ' ', strip_tags(self._content_rendered))
        # Remove new lines with a full stop(.)
        text_only = text_only.replace('\n', '.')
        # Strip single spaces in the beginning of each line
        return text_only.replace('\n ', '\n').strip()[:120]

    def get_tags_list(self):
        return self.tags.split()

    def get_post_detail_url(self):
        return reverse('Blog:post-detail', kwargs={
            'year': self.date_posted.year,
            'month': self.date_posted.month,
            'day': self.date_posted.day,
            'slug': self.slug
        })

    @property
    def hit_count(self):
        url, created = UrlHit.objects.get_or_create(
            url=self.get_post_detail_url())
        # print("absolute url: ", self.get_absolute_url())
        # print("in blog model url: ", url.url)
        # print("in blog model hits: ", url.hits)
        return url.hits
# class Tags(models.Model):
#     tags = models.CharField(max_length=80, blank=True)
