from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import reverse
from PIL import Image

from post.models import Post

# Create your models here.

DEFAULT_IMG = 'profile_pics/default.jpg'
IMG_DIR = 'profile_pics'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(null=True, max_length=140, blank=True)
    image = models.ImageField(default=DEFAULT_IMG,
                              upload_to=IMG_DIR, blank=True)
    public = models.BooleanField(default=False)
    website = models.CharField(null=True, blank=True, max_length=80)
    location = models.CharField(null=True, max_length=200, blank=True)
    join_date = models.DateTimeField(auto_now_add=True)
    bookmarked_posts = models.ManyToManyField(Post)
    # facebook = models.URLField(max_length=200, null=True, blank=True, default='')
    twitter = models.URLField(
        max_length=200, null=True, blank=True, default='')
    instagram = models.URLField(
        max_length=200, null=True, blank=True, default='')
    linkedin = models.URLField(
        max_length=200, null=True, blank=True, default='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_img_path = self.image.path

    def __str__(self):
        return f'{self.user.username} Profile'

    def get_absolute_url(self):
        return reverse("post:author-posts", kwargs={"username": self.user.username})

    def get_bookmarked_posts(self):
        return self.bookmarked_posts.all().order_by('-date_published').values_list('id', flat=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image.path != self.__original_img_path:
            with Image.open(self.image.path) as img:
                if(img.height > 300 or img.width > 300):
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.image.path)
