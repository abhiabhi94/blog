from django.db import models
from django.contrib.auth.models import User
from PIL import Image
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(default='anonymous', max_length=100)
    bio = models.CharField(null=True, max_length=140, blank=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics', blank=True)
    # email = models.EmailField(null=True)
    public = models.BooleanField(default=False)
    website = models.URLField(null=True, blank=True)
    location = models.CharField(null=True, max_length=200, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)
        if(img.height > 300 or img.width > 300):
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
