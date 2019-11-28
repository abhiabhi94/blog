import re
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

# from django.contrib.messages import messages

# Create your models here.


class Category(models.Model, ModelMeta):
    category_name = models.CharField(help_text=(
        "Name of the category. ex-Science, Technology"), max_length=50, unique=True)
    category_info = models.TextField(help_text=(
        "Description of the category."), max_length=5000, unique=True)
    date_created = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    # author of this category.
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    _metadata = {
        'Category': 'category_name',
        'Info': 'category_info'
    }

    def __str__(self):
        '''helps in showing name in foreign key field instead of category object'''
        return self.category_name


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
    # tags = models.ManyToManyField(Tags)
    tags = models.CharField(
        help_text='Enter tags separated by spaces. Do not enter more than 5 tags', max_length=80, default='', blank=True)
    date_posted = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(
        Category, null=True, on_delete=models.SET_NULL)
    publish = models.BooleanField(default=False)
    thumbnail = models.ImageField(
        default='default.jpg', upload_to='profile_pics', blank=True)
    _metadata = {
        'title': 'title',
        'description': 'get_short_des',
        'keywords': 'get_tags_list',
    }

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        self.tags = self.tags.lower()
        # if self.short_des:
        #     pass
        # else:
        #     # self.short_des = ('.').join(self.content.split('.')[:5])
        #     self.short_des = self._content_rendered[:300]
        # self.tags = self.create
        # try:
        #     if(type(eval(self.tags))!=list):
        #         pass
        # except:
        #     self.tags = self.tags.lower().split()
        super(*args, **kwargs).save()
        img = Image.open(self.thumbnail.path)
        if(img.height > 350 or img.width > 350):
            output_size = (350, 350)
            img.thumbnail(output_size)
            img.save(self.thumbnail.path)

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
