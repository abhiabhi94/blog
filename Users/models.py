from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from Blog.models import Post
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(null=True, max_length=140, blank=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics', blank=True)
    public = models.BooleanField(default=False)
    website = models.CharField(null=True, blank=True, max_length=80)
    location = models.CharField(null=True, max_length=200, blank=True)
    join_date = models.DateTimeField(auto_now_add=True)
    bookmarked_posts = models.ManyToManyField(Post)

    def __str__(self):
        return f'{self.user.username} Profile'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)
        if(img.height > 300 or img.width > 300):
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
