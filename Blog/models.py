from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.template.defaultfilters import slugify
# from django.contrib.messages import messages

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(default='', max_length=80)
    content = models.TextField()
    tags = models.CharField(max_length=80, blank=True)
    date_posted = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    publish = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        self.tags = self.tags.lower()
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

# class Tags(models.Model):
#     tags = models.CharField(max_length=80, blank=True)

