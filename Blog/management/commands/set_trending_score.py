import sys

from django.core.management import BaseCommand
from django.utils import timezone

from Blog.models import Post


class Command(BaseCommand):
    help = "Set Trending score"

    def handle(self, *args, **options):
        posts = Post.objects.all()
        for post in posts:
            post.set_trending_score()
        sys.stdout.write(self.style.SUCCESS(
            f'{timezone.now()}: Successfully updated trending score for {len(posts)} posts\n'))
