from datetime import datetime, timedelta

from django.core.paginator import Paginator
from hitcount.models import Hit
from validate_email import validate_email

from post.models import Post


def email_verification(email):
    """Verify whether an email is legit or not"""
    return validate_email(email_address=email, check_regex=True, check_mx=True)


def get_font_cloud(obj, F=5.0, f=1.0):
    """
    Returns a font-cloud based upon the sorted dictionary received.
    Max font-size is 5{rem}
    Min font-size is 1{rem}
    In-between values are calculated based upon linear distribution{ax+b}.
    """
    V = list(obj.values())[0]
    v = 1
    diff = V - v
    b = (f * V - F * v) / diff
    a = (F-f) / diff

    return {key: (val, f'{val*a + b:.3f}' + 'rem') for (key, val) in obj.items()}


def trending(objects=None, start=datetime.today(), interval={'days': 30}, top_n=5):
    """
    Args:
        objects: the queryset to be used for calculation.(If skipped, all published posts are considered.)
        interval: the interval to be considered for calculation.
        top_n: no. of trending values required (default:).
        start: starting time (default:datetime.now()).
        Note: Today will also be considered for calculation.
    Returns:
        The top_n trending values considering {interval} days.
        e.g. For a post with 24 views today(e.g. 24), 25 views on 23th, 220 views on 22nd..
        score = 24/1 + 25/2 + 220/3 + ...(views on the day)/(difference b/w today and that day)
    """
    if objects is None:
        objects = Post.objects.get_published()
    max_score = 0
    for obj in objects:
        # Initialising the score attribute with the view value of current day
        setattr(obj, 'score', Hit.objects.filter(
            hitcount=obj.hit_count, created__contains=start.date()).count())
        # If total views are 0, there's no point in processing any further
        if not obj.views:
            obj.score = 0
            continue

        prev_date = start.date()

        for day in range(1, interval['days']):
            prev_date = prev_date - timedelta(days=1)

            # No point in finding views if the post wasn't published
            if prev_date < obj.date_published.date():
                break

            views = Hit.objects.filter(
                hitcount=obj.hit_count, created__contains=prev_date).count()
            obj.score += views / (day + 1)

    max_score = max(objects, key=lambda obj: obj.score).score
    # Check if max_score is 0 or not
    if max_score:  # Normalizing the score
        for obj in objects:
            obj.score = obj.score / max_score
    return sorted(objects, key=lambda obj: obj.score, reverse=True)[:top_n]


def paginate_util(request, objects, paginate_by, kwargs):
    # Show {paginate_by} objects per page
    paginator = Paginator(objects, paginate_by)
    page = request.GET.get('page')
    objects = paginator.get_page(page)
    if paginator.num_pages > 1:  # no point in paginating if there is only one page.
        kwargs['is_paginated'] = True
    kwargs['page_obj'] = objects
    return objects
