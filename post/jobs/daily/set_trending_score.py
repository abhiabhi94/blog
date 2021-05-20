"""
Daily set Trending scoore job.
Can be run as a cronjob to set trending score for instances of
the Post model.
"""

from django_extensions.management.jobs import DailyJob


class Job(DailyJob):
    help = "Django Daily Cleanup Job"

    def execute(self):
        from django.core import management
        management.call_command("set_trending_score")
