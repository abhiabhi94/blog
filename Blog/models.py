import os
from datetime import timedelta
from enum import IntEnum, unique
from io import BytesIO

from ckeditor_uploader.fields import RichTextUploadingField
from comment.models import Comment
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.html import strip_spaces_between_tags, strip_tags
from django.utils.translation import gettext_lazy as _
from hitcount.models import HitCount, HitCountMixin
from meta.models import ModelMeta
from PIL import Image
from taggit_autosuggest.managers import TaggableManager

from Blog.managers import PostManager

DEFAULT_IMG = 'default.jpg'
IMG_DIR = 'blog'


class Category(models.Model, ModelMeta):
    name = models.CharField(help_text=(
        _("Name of the category. ex-Coding, Robotics")), max_length=50, unique=True)
    slug = models.SlugField(default=slugify(name), max_length=80, unique=True)
    info = models.TextField(help_text=(
        _("Description of the category.")), max_length=5000)
    date_created = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    # author of this category.
    author = models.ForeignKey(User, null=True, limit_choices_to={
                               'is_superuser': True}, on_delete=models.SET_NULL)
    _metadata = {
        'Category': 'name',
        'Info': 'info'
    }

    class Meta:
        verbose_name_plural = _('Categories')

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        """helps in showing name in foreign key field instead of category object"""
        return self.name


class Post(models.Model, ModelMeta, HitCountMixin):

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        self.__original_title = self.title
        self.__original_img_path = self.image.path

    @unique
    class Status(IntEnum):
        DRAFT = -1
        QUEUE = 0
        PUBLISH = 1

    state_choices = [
        (Status.DRAFT.value, _('Draft')),
        (Status.QUEUE.value, _('Queue')),
        (Status.PUBLISH.value, _('Publish')),
    ]

    title = models.CharField(
        help_text=_('Try to keep the title short, within 80 characters.'), max_length=80, unique=True)
    slug_change = models.BooleanField(
        default=False, verbose_name=_('Change Slug'))
    slug = models.SlugField(default='', max_length=80, unique=True)
    content = RichTextUploadingField()
    tags = TaggableManager(blank=True)
    date_created = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, limit_choices_to={
                               'groups__name': 'editor'})
    category = models.ForeignKey(
        Category, null=True, on_delete=models.SET_NULL)
    state = models.SmallIntegerField(
        choices=state_choices, default=Status.DRAFT.value)
    date_published = models.DateTimeField(
        null=True, blank=True)
    featured = models.BooleanField(default=False)
    image = models.ImageField(help_text=_('Do not forget to change this before publishing.'),
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
    comments = GenericRelation(Comment)
    trending_score = models.FloatField(default=0.0)

    objects = PostManager()

    _metadata = {
        'title': 'title',
        'description': '_get_meta_description',
        'keywords': 'get_tags_list',
        'og_author': '_get_meta_author',
        'image': '_get_meta_image',
        'url': 'get_detail_url',
    }

    def _get_meta_image(self):
        """Returns url of the image for meta"""
        if self.thumbnail:
            return self.thumbnail.url

    def _get_meta_author(self):
        """Returns full name of author for meta"""
        return self.author.get_full_name()

    def _get_meta_description(self):
        """Return a short description for meta by removing tags"""
        description = strip_tags(strip_spaces_between_tags(self.content[:200]))
        return description[:150]

    def clean(self):
        """provides custom validation for images before uploading"""

        if self.__original_img_path != self.image.path:

            MIN_IMG_WIDTH, MIN_IMG_HEIGHT = (700, 400)
            MAX_IMG_WIDTH, MAX_IMG_HEIGHT = (7680, 7680)

            img = self.image
            # print('width:', img.width, '\theight:', img.height)
            if img is None:
                raise ValidationError(_('Image not present'), code='invalid')
            if img.width < MIN_IMG_WIDTH:
                raise ValidationError(
                    _(f'Image width should not be less than {MIN_IMG_WIDTH}, \
                        yours width was {img.width}'), code='invalid')
            if img.width > MAX_IMG_WIDTH:
                raise ValidationError(
                    _(f'Image width should not be greater than {MAX_IMG_WIDTH}, \
                        yours width was {img.width}'), code='invalid')
            if img.height < MIN_IMG_HEIGHT:
                raise ValidationError(
                    _(f'Image height should not be less than {MIN_IMG_HEIGHT}, \
                        yours height was {img.height}'), code='invalid')
            if img.height > MAX_IMG_HEIGHT:
                raise ValidationError(
                    _(f'Image height should not be greater than {MAX_IMG_HEIGHT}, \
                        yours height was {img.height}'), code='invalid')

    def save(self, *args, **kwargs):
        """
        1. slugify the title
        2. Sets the date_publish when the publish flag is set for the first time.
        3. compress and resize images to make thumbnails and full size images
        """

        if self.slug_change or (not self.slug):
            self.slug = slugify(self.title)
            # reset the field
            self.slug_change = False

        # Save the publish date when the flag is set for the first time.
        if self.state == self.Status.PUBLISH and self.date_published is None:
            self.date_published = timezone.now()

        super(Post, self).save(*args, **kwargs)

        if self.__original_img_path != self.image.path:
            # remove '.' form the string(e.g '.gif')
            ext = os.path.splitext(self.image.name)[-1][1:]
            if ext.lower() == 'gif':  # do not compress GIF images
                self.thumbnail.save(
                    self.image.name, File(self.image), save=False)
            else:
                # JPG isn't allowed in Pillow
                extension = 'JPEG' if ext.lower() == 'jpg' else ext.upper()

                with Image.open(self.image.path) as img:
                    thumbnail_size, full_view_size = (350, 350), (800, 800)
                    img_thumbnail = img.copy()  # thumbnail changes in place

                    # for list and card view
                    img_thumbnail.thumbnail(thumbnail_size, Image.ANTIALIAS)
                    thumbnail_name = self._image_name('_thumbnail')
                    blob = BytesIO()
                    img_thumbnail.save(blob, format=extension,
                                       quality=75, optimize=True)
                    self.thumbnail.save(thumbnail_name, File(blob), save=False)

                    # for detail view
                    img.thumbnail(full_view_size, Image.ANTIALIAS)
                    img.save(self.image.path, quality=75, optimize=True)

            super(Post, self).save(*args, **kwargs)

    def _image_name(self, modifier):
        """
        modifier - used for changing the name for image
        view - if true return url for template else return path for saving.
        """
        name, extension = os.path.splitext(self.image.name)
        return name + modifier + extension

    def __str__(self):
        return self.title

    def get_preview_url(self) -> str:
        return reverse_lazy('Blog:post-preview', kwargs={
            # 'year': self.date_published.year,
            # 'month': self.date_published.month,
            # 'day': self.date_published.day,
            'slug': self.slug
        })

    def get_tags_list(self):
        return self.tags.all()

    def get_detail_url(self):
        return reverse_lazy('Blog:post-detail', kwargs={
            'year': self.date_published.year,
            'month': self.date_published.month,
            'day': self.date_published.day,
            'slug': self.slug
        })

    @property
    def views(self):
        # return views only if the view is published
        if self.state == self.Status.PUBLISH.value:
            return self.hit_count.hits
        return 0

    def _get_last_n_day_view_per_day(self, n=30):
        """
        Returns a dictionary of views for the last n days.
        e.g {
            1: 20,
            2: 30,
            ...
            31: 200
        }
        """
        if self.date_published is not None:
            diff = 0
            now = timezone.now()
            hitcount = HitCount.objects.get_for_object(self)
            dt_diff = now - timedelta(days=diff)
            hits = {}
            while(self.date_published <= dt_diff and diff < n):
                hits[dt_diff.day] = hitcount.hit_set.filter(created__date=dt_diff.date()).count()
                diff += 1
                dt_diff -= timedelta(diff)
            return hits

    def set_trending_score(self):
        last_month_hits = self._get_last_n_day_view_per_day()
        if last_month_hits:
            self.trending_score = sum([v/k for k, v in last_month_hits.items()])
            self.save(update_fields=['trending_score'])
