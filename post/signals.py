from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver
from hitcount.models import Hit

from post.models import Post


@receiver(post_save, sender=Hit)
def adjust_trending_score(sender, instance, created, raw, using, update_fields, **kwargs):
    post = instance.hitcount.content_object
    if created and isinstance(post, Post):
        post.trending_score = F('trending_score') + 1
        post.save(update_fields=['trending_score'])
