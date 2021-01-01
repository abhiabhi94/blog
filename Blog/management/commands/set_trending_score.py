from django.core.management import BaseCommand

from Blog.models import Post


class Command(BaseCommand):
    help = "Set Trending score"

    def handle(self, *args, **options):
        for post in Post.objects.all():
            post.set_trending_score()
