from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.template.defaultfilters import slugify
# from django.contrib.messages import messages

# Create your models here.
class Post(models.Model):
    title = models.CharField(help_text='Try to keep the title short, within 80 characters.', max_length=80, unique=True)
    slug = models.SlugField(default='', max_length=80)
    short_des = models.TextField(help_text=('This will be displayed on the home page.'
                                    'If you leave it blank, the first 50 words from your article will be displayed.'
                                    'It can not be more than 50 words'),
                                    default='', max_length=500, blank=True
                                )
    content = models.TextField()
    # tags = models.ManyToManyField(Tags)
    tags = models.CharField(help_text='Enter tags separated by spaces. Do not enter more than 5 tags', max_length=80, default='', blank=True)
    date_posted = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    publish = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        self.tags = self.tags.lower()
        if self.short_des:
            pass
        else:
            # self.short_des = ('.').join(self.content.split('.')[:5])
            self.short_des = self.content[:300]
        # self.tags = self.create
        # try:
        #     if(type(eval(self.tags))!=list):
        #         pass
        # except:
        #     self.tags = self.tags.lower().split()
        super(*args, **kwargs).save()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('Blog:post-preview', kwargs={'slug':self.slug})

    def get_tags_list(self):
        return self.tags.split()

class Tags(models.Model):
    tags = models.CharField(max_length=80, blank=True)

