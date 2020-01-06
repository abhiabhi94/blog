import os
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.template.defaultfilters import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from meta.models import ModelMeta
from PIL import Image
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from hitcount.models import HitCountMixin, HitCount
from django.contrib.contenttypes.fields import GenericRelation

DEFAULT_IMG = 'default.jpg'
IMG_DIR = 'blog'


class Category(models.Model, ModelMeta):
    name = models.CharField(help_text=(
        "Name of the category. ex-Science, Technology"), max_length=50, unique=True)
    slug = models.SlugField(default=slugify(name), max_length=80)
    info = models.TextField(help_text=(
        "Description of the category."), max_length=5000)
    date_created = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    # author of this category.
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    _metadata = {
        'Category': 'name',
        'Info': 'info'
    }

    class Meta:
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        self.slug = slugify(self.name)
        super(*args, **kwargs).save()

    def __str__(self):
        '''helps in showing name in foreign key field instead of category object'''
        return self.name


class Post(models.Model, ModelMeta, HitCountMixin):

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        self.__original_title = self.title
        self.__original_tags = self.tags
        self.__original_img_path = self.image.path

    title = models.CharField(
        help_text='Try to keep the title short, within 80 characters.', max_length=80, unique=True)
    slug = models.SlugField(default='', max_length=80)
    content = RichTextUploadingField()
    tags = models.CharField(
        help_text='Enter tags separated by spaces. Do not enter more than 5 tags', max_length=80, default='', blank=True)
    date_created = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(
        Category, null=True, on_delete=models.SET_NULL)
    publish = models.BooleanField(default=False)
    date_published = models.DateTimeField(
        null=True, blank=True)
    featured = models.BooleanField(default=False)
    image = models.ImageField(help_text='Do not forget to change this before publishing',
                              default=DEFAULT_IMG, upload_to=IMG_DIR, blank=True)
    thumbnail = models.ImageField(default=DEFAULT_IMG, blank=True)
    # adding a generic relationship makes sorting by Hits possible:
    # MyModel.objects.order_by("hit_count_generic__hits")
    hit_count_generic = GenericRelation(
        HitCount,
        object_id_field='object_pk',
        content_type_field='content_type',
        related_query_name='hit_count_generic',
    )

    _metadata = {
        'title': 'title',
        # 'description': 'content',
        'keywords': 'get_tags_list',
        'og_author': '_get_meta_author',
        'image': '_get_meta_image',
        'url': 'get_absolute_url',
    }

    def _get_meta_image(self):
        '''Returns url of the image for meta'''
        if self.image:
            return self.image.url

    def _get_meta_author(self):
        '''Returns full name of author for meta'''
        return self.author.get_full_name()

    def clean(self):
        '''provides custom validation for images before uploading'''

        if self.__original_img_path != self.image.path:

            MIN_IMG_WIDTH, MIN_IMG_HEIGHT = (700, 400)
            MAX_IMG_WIDTH, MAX_IMG_HEIGHT = (7680, 4320)

            img = self.image
            # print('width:', img.width, '\theight:', img.height)
            if img is None:
                raise ValidationError(f'Image not present', code='invalid')
            if img.width < MIN_IMG_WIDTH:
                raise ValidationError(
                    f'Image width should not be less than {MIN_IMG_WIDTH}, yours width was {img.width}', code='invalid')
            if img.width > MAX_IMG_WIDTH:
                raise ValidationError(
                    f'Image width should not be greater than {MAX_IMG_WIDTH}, yours width was {img.width}', code='invalid')
            if img.height < MIN_IMG_HEIGHT:
                raise ValidationError(
                    f'Image height should not be less than {MIN_IMG_HEIGHT}, yours height was {img.height}', code='invalid')
            if img.height > MAX_IMG_HEIGHT:
                raise ValidationError(
                    f'Image height should not be greater than {MAX_IMG_HEIGHT}, yours height was {img.height}', code='invalid')

    def save(self, *args, **kwargs):
        '''
        1. slugify the title
        2. save the tags in lower case
        3. Sets the date_publish when the publish flag is set for the first time.
        4. compress and resize images to make thumbnails and full size images
        '''

        if self.__original_title != self.title:
            self.slug = slugify(self.title)
        if self.__original_tags != self.tags:
            self.tags = self.tags.lower()

        super(Post, self).save(*args, **kwargs)

        # Save the publish date when the flag is set for the first time.
        if self.publish and self.date_published is None:
            self.date_published = timezone.now()

        if self.__original_img_path != self.image.path:

            with Image.open(self.image.path) as img:
                thumbnail_size, full_view_size = (350, 350), (800, 800)

                img_thumbnail = img.copy()  # thumbnail changes in place

                # for list and card view
                img_thumbnail.thumbnail(thumbnail_size, Image.ANTIALIAS)
                thumbnail_name = self._image_name('_thumbnail')
                img_thumbnail.save(thumbnail_name, quality=75, optimize=True)

                with open(thumbnail_name, 'rb') as f:
                    data = f.read()

                self.thumbnail.save(
                    thumbnail_name, ContentFile(data), save=False)
                # Remove thumbnail image
                os.remove(thumbnail_name)

                # for detail view
                img.thumbnail(full_view_size, Image.ANTIALIAS)
                img.save(self.image.path, quality=75, optimize=True)

        super(Post, self).save(*args, **kwargs)

    def _image_name(self, modifier):
        '''
        modifier - used for changing the name for image
        view - if true return url for template else return path for saving.
        '''
        new_name = self.image.name.split('.')
        new_name.insert(-1, modifier + '.')  # dont forget extension
        return ''.join(new_name)

    def __str__(self):
        return self.title

    def get_preview_url(self):
        return reverse('Blog:post-preview', kwargs={
            # 'year': self.date_published.year,
            # 'month': self.date_published.month,
            # 'day': self.date_published.day,
            'slug': self.slug
        })

    def get_tags_list(self):
        return self.tags.split()

    def get_detail_url(self):
        return reverse('Blog:post-detail', kwargs={
            'year': self.date_published.year,
            'month': self.date_published.month,
            'day': self.date_published.day,
            'slug': self.slug
        })

    @property
    def views(self):
        # return views only if the view is published
        if self.publish:
            return self.hit_count.hits
        return 0
