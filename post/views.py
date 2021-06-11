import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.syndication.views import Feed
from django.db.models import Count
from django.http import Http404, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from hitcount.views import HitCountDetailView
from meta.views import Meta
from taggit.models import Tag

from post.decorators.restrict_access import require_ajax, require_group
from post.mixins import IsOwnerMixin
from post.models import Category, Post
from post.utils import email_verification, paginate_util
from subscriber.models import Subscriber
from user_profile.models import Profile

"""
Use the name posts for backend purposes.
Use the name articles for frontend purposes.
"""

global paginate_by
# For pages this pagination values will be used
paginate_by = 10

global meta_home
meta_home = Meta(title='HackAdda | Never stop hacking!',
                 description=_(
                     'Stay updated with the latest technology news, articles, and tutorials.'),
                 keywords=[
                     'Hack', 'Robotics', 'Coding',
                     'STEM', 'STEAM', 'Education',
                     'Blog', 'Tinker', 'Kids',
                     'Technology', 'Curiousity'
                 ],
                 url='https://hackadda.com',
                 #  image='',
                 og_type='website',
                 locale='en_US',
                 site_name='HackAdda',
                 twitter_creator='@thehackadda',
                 twitter_site='@thehackadda',
                 og_publisher='https://www.facebook.com/thehackadda',
                 )
# conditional og property - og_author_url, published_time, modified_time, image,
# consider adding other property in future. TODO


BadAJAXRequestException = (
    json.decoder.JSONDecodeError,
    TypeError,
    KeyError,
)


@method_decorator(require_http_methods(['GET']), name='dispatch')
class HomeView(ListView):
    """Return featured, latest, and categories wise articles for the front-page"""

    template_name = 'post/home.html'   # <app>/<model>_<viewtype>.html
    NUM_FEATURED_POSTS = 3
    NUM_LATEST_POSTS = 6
    NUM_CATEGORY_POSTS = 2
    # Categories to displayed on the homepage
    HOME_CATEGORIES = [
        # Use news only when you are updating it regularly.
        # 'news',
        'coding',
        'operating-system',
        'kids',
    ]

    def get_queryset(self):
        return Post.objects.get_published()

    @staticmethod
    def remove_duplicates(current, unique, top_n):
        """
        Returns unique posts in current after removing duplicate objects from it.
        Set difference is calculated here as a part of list comphrehension in order to maintain order.
        """
        current_unique = [i for i in current if i not in unique][:top_n]

        # No need to use sets: both are unique and non-intersectino
        unique = current_unique + unique
        return current_unique, unique

    def get_featured_posts(self):
        """
        Returns top_n featured posts
        where top_n is self.NUM_FEATURED_POSTS
        """
        top_n = self.NUM_FEATURED_POSTS

        return Post.objects.get_published().filter(featured=True)[:top_n]

    def get_latest_posts(self):
        """
        Returns top_n latest_posts
        +self.NUM_LATEST_POSTS latest posts for
        +self.NUM_FEATURED_POSTS is for checking duplicacy with featured articles
        """
        top_n = self.NUM_LATEST_POSTS + self.NUM_FEATURED_POSTS

        return Post.objects.get_published()[:top_n]

    def get_category_posts(self, slug, index):
        """
        Returns top_n posts under a certain category.
        for top_n = + self.NUM_FEATURED_POSTS is for featured articles
                    + self.NUM_LATEST_POSTS is for latest articles
                    + self.NUM_CATEGORY_POSTS * (index+1) is for extra articles in case of duplicacy with the
                    above categories.
                    1 is added to index since it starts from 0.
        """

        top_n = self.NUM_FEATURED_POSTS + self.NUM_LATEST_POSTS + \
            self.NUM_CATEGORY_POSTS * (index + 1)
        return Post.objects.get_published().filter(category__slug=slug)[:top_n]

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['meta'] = meta_home
        posts_unique = context['featured_posts'] = list(self.get_featured_posts())

        latest_posts = list(self.get_latest_posts())
        context['latest_posts'], posts_unique = self.remove_duplicates(
            latest_posts, posts_unique, self.NUM_LATEST_POSTS)

        # All category objects will be appended in this list
        categories = Category.objects.filter(slug__in=self.HOME_CATEGORIES)

        category_result = {}
        for index, category in enumerate(categories):
            category_posts = list(self.get_category_posts(category.slug, index))
            category_posts_unique, posts_unique = self.remove_duplicates(
                category_posts, posts_unique, self.NUM_CATEGORY_POSTS)
            category_result[category] = category_posts_unique

        context['category'] = category_result
        if self.request.user.is_authenticated:
            context['profile'] = self.request.user.profile

        return context


@require_http_methods(['POST'])
@require_ajax()
def subscribe(request):
    """
    adds emails to the model Subscriber after verifying legit emails only on POST requests.
    Returns Jsonresponse with properties response and status.
    """
    data = {'msg': '', 'email': '', 'status': -1}
    if request.method == 'POST':
        email = request.POST['email']
        data['email'] = email
        if email_verification(email):
            try:
                __, created = Subscriber.objects.get_or_create(email=email)
                if created:
                    data['msg'] = ' is now registered successfully with us'
                    data['status'] = 0
                else:
                    data['msg'] = ' is already registered with us'
            except Exception:
                data['status'] = 1
                data['msg'] = 'There seems to be an issue on our side. Please retry.'

            data['msg'] = _(data['msg'])
            return JsonResponse(data)

        data['msg'] = _(' is not a valid email')
        return JsonResponse(data)
    return HttpResponseBadRequest


@method_decorator(require_http_methods(['GET']), name='dispatch')
class FeaturedPostListView(ListView):
    """Returns a list view of featured posts."""

    template_name = 'post/post_list_featured.html'
    context_object_name = 'posts'
    paginate_by

    def get_queryset(self):
        return Post.objects.get_published().filter(featured=True)

    def get_context_data(self, **kwargs):
        context = super(FeaturedPostListView, self).get_context_data(**kwargs)
        context['meta'] = Meta(title='Featured Articles | HackAdda',
                               description='Read featured articles on HackAdda',
                               keywords=meta_home.keywords + ['featured'])
        return context


@method_decorator(require_http_methods(['GET']), name='dispatch')
class AuthorPostListView(ListView):
    # model = Post
    template_name = 'post/author_posts.html'   # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.get_published().filter(author=user)

    def get_context_data(self, **kwargs):
        context = super(AuthorPostListView, self).get_context_data(**kwargs)
        author = get_object_or_404(User, username=self.kwargs.get('username'))
        context['author'] = author
        name = author.get_full_name()
        context['meta'] = Meta(title=f'{name.title()} | HackAdda',
                               description=f'Articles authored by {name}',
                               og_author=f'{name}',
                               keywords=meta_home.keywords)
        context['profile'] = author.profile
        return context


@method_decorator(require_http_methods(['GET']), name='dispatch')
@method_decorator(require_group(group_name='editor'), name='dispatch')
class UserPostListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Post
    template_name = 'post/user_posts.html'   # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 10

    def test_func(self):
        """Check if the logged in user is viewing their post"""
        return self.request.user.username == self.kwargs.get('username')

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user)
        tab = self.kwargs.get('tab', 'draft')

        if tab == 'queued':
            return Post.objects.get_queued(author=user)
        elif tab == 'published':
            return Post.objects.get_published(author=user)
        else:  # for draft
            return Post.objects.get_draft(author=user)

    def get_context_data(self, **kwargs):
        context = super(UserPostListView, self).get_context_data(**kwargs)

        user = get_object_or_404(User, username=self.request.user)
        name = user.get_full_name()
        context['tab_type'] = self.kwargs.get('tab', 'draft')
        context['meta'] = Meta(title=f'{name} | HackAdda',
                               description=f'Articles authored by {name}',
                               og_author=f'{name}',
                               keywords=meta_home.keywords)
        return context


@method_decorator(require_http_methods(['GET']), name='dispatch')
class UserPostBookmark(LoginRequiredMixin, ListView):
    model = User
    context_object_name = 'posts'
    template_name = 'post/user_bookmarks.html'
    paginate_by = 10
    # queryset = User.objects.get_bookmarked_posts

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        if user == self.request.user:
            return user.profile.bookmarked_posts.all().order_by('-date_published')
        #  Return HTTP Error: "You should be logged in as the user" ###
        raise Http404(
            f'You should be signed in as {user} to view this page')

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)  # TODO
        context['profile'] = self.request.user.profile
        return context


@method_decorator(require_http_methods(['GET']), name='dispatch')
class PostDetailView(HitCountDetailView, DetailView):
    queryset = Post.objects.get_published()
    context_object_name = 'post'
    count_hit = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meta'] = self.get_object().as_meta(self.request)
        if self.request.user.is_authenticated:
            context['profile'] = self.request.user.profile
        return context


@require_http_methods(['POST'])
@require_ajax()
def get_recommended_posts(request):
    """
    Condition:
        Works only for requests which are POST and AJAX.

    Args:
        post: the object whose recommended posts are request
        top_n: No. of recommended articles required

    Returns:
        Return {n} posts with tags related to the current post.
        if similar posts are lesser, most trending posts are returned in their position.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.POST.get('data', None))
            slug = data.get('slug', None)
            num = int(data.get('top_n', None))

        except (BadAJAXRequestException + (ValueError,)):
            return HttpResponseBadRequest(
                _('Wrong Request Format for post request'))

        template_name = 'post_latest_home.html'
        order = '-trending_score'
        context = {}
        current_post = get_object_or_404(Post, slug=slug)
        recommended_posts_ids = [
            post.id for post in current_post.tags.similar_objects()]
        all_published_posts = Post.objects.get_published()
        recommended_posts = all_published_posts.filter(
            id__in=recommended_posts_ids).order_by(order)[:num]
        length = len(recommended_posts)
        # add trending posts if similar posts are less.
        if length < num:
            # exclude the current and already obtained similar posts above
            recommended_posts = recommended_posts.union(
                all_published_posts.exclude(slug=slug)
                .exclude(id__in=recommended_posts_ids)
                .order_by(order)[:num-length]
                )
        context['posts'] = recommended_posts
        context['recommend'] = True
        return render(request, template_name, context)


@method_decorator(require_http_methods(['GET', 'POST']), name='dispatch')
@method_decorator(require_group(group_name='editor'), name='dispatch')
class PostCreateView(CreateView):
    model = Post
    fields = ['title', 'content', 'image', 'tags', 'category']

    def form_valid(self, form):
        form.instance.author = self.request.user
        if self.request.method == 'POST':
            form.instance.state = Post.Status.DRAFT.value
            messages.success(
                self.request, 'Your article has been saved.')
        else:
            return HttpResponseBadRequest('Wrong request method')
        return super().form_valid(form)

    def get_success_url(self):
        """Since there's no absolute url in the model, this function provides a redirect on form success."""
        slug = self.object.slug
        if 'draft' in self.request.POST:  # draft option was selected
            return reverse_lazy('post:draft-post-update', kwargs={'slug': slug})
        elif 'preview' in self.request.POST:
            return reverse_lazy('post:post-preview', kwargs={'slug': slug})
        else:
            return HttpResponseBadRequest('Wrong request!!!')


@method_decorator(require_http_methods(['GET', 'POST']), name='dispatch')
class DraftPostUpdateView(LoginRequiredMixin, IsOwnerMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'image', 'tags', 'category']

    def form_valid(self, form):
        """
        Checks whether the user logged in is the one updating the post.
        Checks whether the user is authorised to update the article(only members of the group `editor` are allowed)
        It then reverses the published state so that admin's approval is required before publishing the updated post.
        """
        post = self.get_object()
        if self.request.user == post.author:
            messages.success(
                self.request, 'Your article has been saved.')
        else:
            messages.warning(
                self.request, 'You are not allowed to update this post.')
            return redirect('post:home')
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Since there's no absolute url in the model, this function provides a redirect on form success."""
        slug = self.object.slug

        if 'draft' in self.request.POST:  # draft option was selected
            return reverse_lazy('post:draft-post-update', kwargs={'slug': slug})
        elif 'preview' in self.request.POST:
            return reverse_lazy('post:post-preview', kwargs={'slug': slug})
        else:
            return HttpResponseBadRequest('Wrong request!!!')


@method_decorator(require_http_methods(['GET', 'POST']), name='dispatch')
@method_decorator(require_group(group_name='editor'), name='dispatch')
class PostUpdateView(IsOwnerMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'image', 'tags', 'category']

    def form_valid(self, form):
        """
        Checks whether the user logged in is the one updating the post.
        Checks whether the user is authorised to update the article(only members of the group `editor` are allowed)
        It then reverses the published state so that admin's approval is required before publishing the updated post.
        """
        post = self.get_object()
        if self.request.user == post.author:
            # Currently we can't keep more than 1 version of a Post
            # Hence when the preview option is selected, the state is changed to draft, and the post is unpublished
            # I(Abhyudai), currently expect the author to make review the changes soon
            # in the next view and queue(editor) or publish them(superuser)
            # I know this is a dangerous.

            # if publish option is choosen
            if 'publish' in self.request.POST:
                # publish for superuser and queued for others
                if self.request.user.is_superuser:
                    form.instance.state = Post.Status.PUBLISH.value  # state -> published
                    messages.success(
                        self.request, 'Your article has been published.')
                else:
                    form.instance.state = Post.Status.QUEUE.value  # state -> queued
                    messages.success(
                        self.request, 'Your article has been submitted for approval.')
            # otherwise set the state to draft
            else:
                form.instance.state = Post.Status.DRAFT.value
        else:
            messages.warning(
                self.request, 'You are not allowed to update this post.')
            return redirect('post:home')

        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Since there's no absolute url in the model, this function provides a redirect on form success."""
        if 'publish' in self.request.POST:
            return reverse_lazy('post:home')
        elif 'preview' or 'draft' in self.request.POST:  # for both preview and draft, show preview
            return reverse_lazy('post:post-preview', kwargs={'slug': self.object.slug})
        else:
            return HttpResponseBadRequest('Wrong request!!!')


@method_decorator(require_http_methods(['GET', 'POST']), name='dispatch')
@method_decorator(require_group(group_name='editor'), name='dispatch')
class PostDeleteView(SuccessMessageMixin, LoginRequiredMixin, IsOwnerMixin, DeleteView):
    model = Post
    fields = ['title', 'content', 'image', 'tags', 'category']
    success_url = reverse_lazy('post:home')
    success_message = "Post %(title)s was removed successfully"

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post has been deleted successfully!!!')
        return super().form_valid(form)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super().delete(request, *args, **kwargs)


@require_http_methods(['GET'])
def about(request):
    context = {}
    template_name = 'post/about.html'
    context['meta'] = Meta(title='About | HackAdda',
                           description='A glance at the stuff HackAdda offers',
                           keywords=meta_home.keywords)
    return render(request, template_name, context)


@require_group(group_name='editor')
@require_http_methods(['GET', 'POST'])
def preview(request, slug):
    post = get_object_or_404(Post, slug=slug)
    # ajax requests are coming here for some weird reason
    if request.method == 'POST':
        """Submit post for review"""
        is_superuser = request.user.is_superuser
        if request.user == post.author or is_superuser:
            if is_superuser:  # publish directly for superuser
                post.state = Post.Status.PUBLISH.value  # state -> published
                messages.success(
                    request, f'The article {post.title} has been published')
            else:
                post.state = Post.Status.QUEUE.value  # state -> queued
                messages.success(
                    request, f'Your article {post.title} has been submitted for approval.')

            post.save()
        else:
            messages.warning(
                request, 'You are not allowed to update this post.')
        return redirect('post:home')
        # return reverse('post:my-posts', kwargs={'username': request.user, 'tab': 'drafts'})
    else:
        template_name = 'post/post_preview.html'
        return render(request, template_name, {'post': post})


@require_http_methods(['POST'])
@require_ajax()
def bookmark_post(request):
    """
    Returns
        A JSON response
            data:   message: str
                        The message
                    status: int
                        -1 -> user not logged in
                        0 -> post successfully addes as bookmark
                        1 -> post successfully removed from bookmark
    """
    if request.method == 'POST':
        data = {'message': '', 'status': 1}
        if request.user.is_authenticated:
            try:
                slug = json.loads(request.body.decode('utf-8'))['data']
            except BadAJAXRequestException:
                return HttpResponseBadRequest(
                    _('Wrong Request Format for post request'))

            pk = get_object_or_404(Post, slug=slug).id
            b_post = Profile.objects.filter(
                user=request.user, bookmarked_posts=pk)
            if not b_post:
                request.user.profile.bookmarked_posts.add(pk)
                data['message'] = 'Post bookmarked'
                data['status'] = 0
            else:
                request.user.profile.bookmarked_posts.remove(pk)
                data['message'] = 'Post removed from bookmarks'
            return JsonResponse(data)

        # redirect with a message
        data['status'] = -1
        messages.info(
            request, 'You need to be logged in to bookmark a post')
        return JsonResponse(data)


@method_decorator(require_http_methods(['GET']), name='dispatch')
class TaggedPostListView(ListView):
    template_name = 'post/post_tagged.html'   # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'

    def get_queryset(self):
        post_list = Post.objects.get_published().filter(
            tags__slug=self.kwargs.get('slug').lower())
        if post_list:
            return post_list
        raise Http404('Tag not present')

    ordering = ['-date_published']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug').lower()
        tag = get_object_or_404(Tag, slug=slug).name
        context['meta'] = Meta(title=f'{tag.title()} | HackAdda',
                               description=f'Read articles with the tag {tag} on Hackadda',
                               keywords=meta_home.keywords + [tag])
        context['tag'] = tag
        return context


@require_http_methods(['GET', 'POST'])
def get_latest_posts(request, **kwargs):
    @require_ajax()
    def get_for_sidebar(request, **kwargs):
        template_name = 'post_title.html'
        try:
            top_n = int(json.loads(request.POST.get('data'))['top_n'])
        except BadAJAXRequestException:
            return HttpResponseBadRequest(
                _('Wrong Request Format for post request')
                )
        posts = Post.objects.get_published()[:top_n]
        return render(request, template_name, {'posts': posts})

    def get_for_page(request, **kwargs):
        template_name = 'post/post_list_latest.html'
        global paginate_by
        posts = Post.objects.get_published()
        kwargs['posts'] = paginate_util(request, posts, paginate_by, kwargs)
        kwargs['meta'] = Meta(title='Latest Articles| HackAdda',
                              description='Read latest articles on HackAdda',
                              keywords=meta_home.keywords + ['latest'])
        return render(request, template_name, kwargs)

    if request.method == 'POST':
        return get_for_sidebar(request, **kwargs)
    if request.method == 'GET':
        return get_for_page(request, **kwargs)


@method_decorator(require_http_methods(['GET', 'POST']), name='dispatch')
class GetTags(View):
    """
    1. Get request is used for top tags(mostly used)
    2. Post request is used for displaying the top_n tags in the sidebar
    """

    context = {}

    @staticmethod
    def _get_top_tags_qs():
        # Filter published posts -> extract values from name and slug fields -> annotate by count -> Order
        return Tag.objects.filter(post__in=Post.objects.get_published()).values(
            'name', 'slug', count=Count('name')).order_by('-count')

    @method_decorator(require_ajax(), name='dispatch')
    def post(self, request, *args, **kwargs):
        template_name = 'tags.html'
        try:
            top_n = int(json.loads(request.POST.get('data'))['top_n'])
        except (BadAJAXRequestException + (ValueError,)):
            return HttpResponseBadRequest(_("Wrong Request Format"))

        finally:
            # For showing option of view more on sidebar
            self.context['ajax'] = True
        self.context['tags'] = self._get_top_tags_qs()[:top_n]

        return render(request, template_name, self.context)

    def get(self, request, *args, **kwargs):
        template_name = 'all_tags.html'
        top_tags = self._get_top_tags_qs()

        self.context['tags'] = top_tags

        # Tag clouds will be probably implemented in a better way
        # in a future release.
        # context['tags'] = get_font_cloud(top_tags_list)
        self.context['meta'] = Meta(
            title='Tags | HackAdda',
            description='List of all Tags on HackAdda',
            keywords=meta_home.keywords + list(top_tags.values_list('name', flat=True))
        )
        return render(request, template_name, self.context)


@method_decorator(require_http_methods(['GET']), name='dispatch')
class CategoryPostListView(ListView):
    # model = Post
    template_name = 'post/post_list_category.html'   # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'

    def get_queryset(self):
        post_list = Post.objects.get_published().filter(
            category__slug=self.kwargs.get('slug').lower())
        if post_list:
            return post_list
        raise Http404('Category not present')

    ordering = ['-date_published']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        category = get_object_or_404(Category, slug=slug)

        context['meta'] = Meta(title=f'{str(category).title()} | HackAdda',
                               description=_(f'Read articles of the category {category} from HackAdda'),
                               keywords=meta_home.keywords + [category])
        context['category'] = category
        return context


@require_http_methods(['GET'])
def get_timewise_list(request, *args, **kwargs):

    template_name = 'post/post_list_time.html'
    paginate_by = 10

    if request.method == 'GET':
        placeholder = datetime.now()  # to use formatting on template layer.
        kwargs = {k: int(v) if v is not None else v for k, v in kwargs.items()}
        placeholder = placeholder.replace(year=kwargs['year'])
        flag_day, flag_month = [1, 1]
        if kwargs['day'] is None:
            if kwargs['month'] is None:
                # both day and month are dummy values
                flag_day, flag_month = [0, 0]
            else:
                # month isn't dummy, day is dummy.
                flag_day, flag_month = [0, 1]
                placeholder = placeholder.replace(month=kwargs['month'])
        else:
            placeholder = datetime(**kwargs)

        args_dict = {}
        args_dict['date_published__year'] = kwargs['year']
        if flag_day:
            args_dict['date_published__day'] = kwargs['day']
        if flag_month:
            args_dict['date_published__month'] = kwargs['month']

        posts = Post.objects.get_published().filter(**args_dict)

        kwargs['date'], kwargs['flag_day'], kwargs['flag_month'] = placeholder, flag_day, flag_month
        kwargs['posts'] = paginate_util(request, posts, paginate_by, kwargs)
        kwargs['meta'] = meta_home
        return render(request, template_name, kwargs)


@method_decorator(require_http_methods(['GET', 'POST']), name='dispatch')
class GetCategory(View):
    """
    Get categories(foreign key) present in post
    1. For get request, all categories are shown in a page.
    2. For post request, top_n categories are shown in the sidebar.
    """
    context = {}

    @staticmethod
    def _get_top_categories_qs():
        # Filter published posts -> extract values from name and slug fields -> annotate by count -> Order
        return Category.objects.filter(post__in=Post.objects.get_published())\
                .values('name', 'slug', count=Count('name'))\
                .order_by('-count')

    @method_decorator(require_ajax(), name='dispatch')
    def post(self, request, *args, **kwargs):
        template_name = 'post/categories.html'
        try:
            top_n = int(json.loads(request.POST.get('data'))['top_n'])
        except (BadAJAXRequestException + (ValueError,),):
            return HttpResponseBadRequest(_("Wrong Request Format"))
        finally:
            self.context['ajax'] = True

        self.context['categories'] = self._get_top_categories_qs()[:top_n]
        return render(request, template_name, self.context)

    def get(self, request, *args, **kwargs):
        template_name = 'all_categories.html'
        top_categories_qs = self._get_top_categories_qs()
        self.context['categories'] = top_categories_qs
        self.context['meta'] = Meta(
            title='Categories | HackAdda',
            description='List of all Categories on HackAdda',
            keywords=meta_home.keywords + list(top_categories_qs.values_list('name', flat=True))
        )
        return render(request, template_name, self.context)


@require_http_methods(['POST'])
@require_ajax()
def get_trending_posts(request):
    """Returns top_n trending post for a given time period for POST requests in AJAX format."""

    if request.method == 'POST':
        template_name = 'post_title.html'
        try:
            top_n = int(json.loads(request.POST.get('data'))['top_n'])
        except (BadAJAXRequestException + (ValueError,)):
            return HttpResponseBadRequest(_("Wrong Request Format"))

        trending_posts = Post.objects.get_published().order_by('-trending_score')[:top_n]
        return render(request, template_name, {'posts': trending_posts, 'meta': meta_home})


class LatestPostRSSFeed(Feed):
    title = 'Latest posts from HackAdda'
    link = ''
    description = meta_home.description

    def items(self, top_n=5):
        return Post.objects.get_published()[:top_n]

    def item_title(self, item):
        return item.title

    def item_author_name(self, item):
        return item.author.get_full_name()

    def item_description(self, item):
        return item.content

    def item_link(self, item):
        return item.get_detail_url()

    def item_categories(self, item):
        return item.get_tags_list()
