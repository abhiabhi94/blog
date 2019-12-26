from validate_email import validate_email
from .models import Post
from datetime import datetime, timedelta
from hitcount.models import Hit
from django.core.paginator import Paginator


def published_posts(order='-date_published'):
    '''
    TODO: support multiple filters.
    returns a list of published posts.
    if no order is given, the posts are ordered by their post date.
    '''
    return Post.objects.filter(publish=True).order_by(order)


def email_verification(email):
    '''Verify whether an email is legit or not'''
    return validate_email(email_address=email, check_regex=True, check_mx=True)


def get_font_cloud(obj, F=5.0, f=1.0):
    '''
    Returns a font-cloud based upon the sorted dictionary received.
    Max font-size is 5{rem}
    Min font-size is 1{rem}
    In-between values are calculated based upon linear distribution{ax+b}.
    '''
    V = list(obj.values())[0]
    v = 1
    diff = V - v
    b = (f * V - F * v) / diff
    a = (F-f) / diff

    # for key, val in obj:
    # obj['key'] = (val, val*a + b)
    return {key: (val, f'{val*a + b:.3f}' + 'rem') for (key, val) in obj.items()}
    # return {key: (val, f'{F*(val-v)/diff + 1:.3f}' + 'rem') for (key, val) in obj.items()}


def trending(objects, start=datetime.today(), interval={'days': 30}, top_n=5):
    '''
    Args:
        interval: the interval to be considered for calculation.
        top_n: no. of trending values required (default:).
        start: starting time (default:datetime.now()).
        Note: Today will also be considered for calculation.

    Returns:
        The top_n trending values considering {interval} days.
        e.g. For a post with 24 views today(e.g. 24), 25 views on 23th, 220 views on 22nd..
        score = 24/1 + 25/2 + 220/3 + ...(views on the day)/(difference b/w today and that day) 
    '''
    max_score = 0
    for obj in objects:
        # Initialising the score attribute with the view value of current day
        setattr(obj, 'score', Hit.objects.filter(
            hitcount=obj.hit_count, created__day=start.day).count())
        prev_date = start
        # print('publish date:', obj.date_published)

        for day in range(1, interval['days']):
            # print('Day:', prev_date.day)
            prev_date = prev_date - timedelta(days=1)

            # No point in finding views if the post wasn't published
            if prev_date.date() < obj.date_published.date():
                break

            views = Hit.objects.filter(
                hitcount=obj.hit_count, created__day=prev_date.day).count()
            # print(f'Views on {prev_date}:', views)
            obj.score += views / (day + 1)

        # print('\nScore for', obj, ':', obj.score)

        # Normalizing the score
        max_score = max(obj.score, max_score)
        obj.score = obj.score / max_score

    # [print(obj, ':\t', obj.score) for obj in objects]
    return sorted(objects, key=lambda obj: obj.score, reverse=True)[:5]


def paginate_util(request, objects, paginate_by, kwargs):
    # Show {paginate_by} objects per page
    paginator = Paginator(objects, paginate_by)
    page = request.GET.get('page')
    objects = paginator.get_page(page)
    if paginator.num_pages > 1:  # no point in paginating if there is only one page.
        kwargs['is_paginated'] = True
    kwargs['page_obj'] = objects
    return objects
