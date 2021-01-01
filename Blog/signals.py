from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F
from hitcount.models import Hit

from Blog.models import Post

@receiver(post_save, sender=Hit)
def adjust_trending_score(sender, instance, created, raw, using, update_fields, **kwargs):
    if created and isinstance(instance, Post):
        instance.trending_score = F('trending_score') + 1
        instanace.save(update_fields=['trending_score'])
