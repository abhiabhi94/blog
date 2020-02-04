import json
from django.views.generic import (ListView,
                                  DetailView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView
                                  )
from django.contrib.auth.models import User
from Users.models import Profile
from django.contrib import messages
from django.shortcuts import (render,
                              redirect,
                              get_object_or_404)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.models import User
from django.http import (JsonResponse,
                         Http404,
                         HttpResponseBadRequest,
                         )
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from collections import Counter
from meta.views import Meta
from datetime import datetime
from django.db import IntegrityError
from django.contrib.syndication.views import Feed
from Blog.models import Post, Category
from Subscribers.models import Subscriber
from hitcount.views import HitCountDetailView
from django.utils import timezone
from Blog.manager import (published_posts,
                          email_verification,
                          get_font_cloud,
                          trending,
                          paginate_util,
                          )
from Blog.decorators.restrict_access import group

"""
Use the name posts for backend purposes.
Use the name articles for frontend purposes.
"""


global meta_home
meta_home = Meta(title='HackAdda | Never stop hacking!',
                 description='Stay updated with the latest technology news, articles, and tutorials.',
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


@method_decorator(require_http_methods(['GET']), name='dispatch')
class HomeView(ListView):
    """Return featured, latest, and categories wise articles for the front-page"""

    template_name = 'Blog/home.html'   # <app>/<model>_<viewtype>.html
    # context_object_name = 'posts'
    # paginate_by = 5
    # posts_unique = {}

    def __init__(self):
        self.NO_FEATURED_POSTS = 3
        self.NO_LATEST_POSTS = 6
        self.NO_CATEGORY_POSTS = 2
        super().__init__()

    def get_queryset(self):
        return published_posts()

    def remove_duplicates(self, current, unique, top_n):
        """
        Returns unique posts in current after removing duplicate objects from it.
        Set difference is calculated here as a part of list comphrehension in order to maintain order.
        """
        # print('values>>>', len(current))
        # print('unique>>>', unique, len(unique), '\n')

        # Find values from current list that aren't inside unique
        current_unique = [i for i in current if i not in unique][:top_n]
        # print('current-unique', current_unique, len(current_unique), '\n')

        """
        Add current_unique and unique
        No need to use sets: both are unique and non-intersecting(current unique is just calculated above))
        """
        unique = current_unique + unique
        # print('unique after union>>>', unique, len(unique), '\n')
        return current_unique, unique

    def get_featured_posts(self):
        """
        Returns top_n featured posts
        where top_n is self.NO_FEATURED_POSTS
        """
        top_n = self.NO_FEATURED_POSTS

        return published_posts().filter(featured=True)[:top_n]

    def get_latest_posts(self):
        """
        Returns top_n latest_posts
        +self.NO_LATEST_POSTS latest posts for
        +self.NO_FEATURED_POSTS is for checking duplicacy with featured articles
        """
        top_n = self.NO_LATEST_POSTS + self.NO_FEATURED_POSTS

        return published_posts()[:top_n]

    def get_category_posts(self, slug, index):
        """
        Returns top_n posts under a certain category.
        for top_n = +self.NO_FEATURED_POSTS is for featured articles
                    +self.NO_LATEST_POSTS is for latest articles
                    +self.NO_CATEGORY_POSTS * (index+1) is for extra articles in case of duplicacy with the above categories.
                    1 is added to index since it starts from 0.
        """

        top_n = self.NO_FEATURED_POSTS + self.NO_LATEST_POSTS + \
            self.NO_CATEGORY_POSTS * (index + 1)
        return published_posts().filter(category__slug=slug)[:top_n]

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['meta'] = meta_home
        posts_unique = context['featured_posts'] = list(
            self.get_featured_posts())
        # posts_unique = context['featured_posts']

        latest_posts = list(self.get_latest_posts())
        context['latest_posts'], posts_unique = self.remove_duplicates(
            latest_posts, posts_unique, self.NO_LATEST_POSTS)

        """
        Categories to displayed on the homepage
        format: all small-case and in slugified form
        """
        home_categories = [
            'kids',
            'coding',
        ]

        # All category objects will be appended in this list
        categories = []

        [categories.append(Category.objects.get(
            slug=category)) for category in home_categories]

        category_result = {}
        for index, category in enumerate(categories):
            category_posts = list(
                self.get_category_posts(category.slug, index))
            category_posts_unique, posts_unique = self.remove_duplicates(
                category_posts, posts_unique, self.NO_CATEGORY_POSTS)
            category_result[category] = category_posts_unique

        context['category'] = category_result
        if self.request.user.is_authenticated:
            context['profile'] = self.request.user.profile
        # print("Featured>>>", context['featured_posts'])
        # print("Latest>>>", context['latest_posts'])
        # print("Categories>>>", context['category'])

        return context


@require_http_methods(['POST'])
def subscribe(request):
    """
    adds emails to the model Subscribers after verifying legit emails only on POST requests.
    Returns Jsonresponse with properties response and status.
    """
    data = {'msg': '', 'email': '', 'status': -1}
    if request.method == 'POST' and request.is_ajax():
        email = request.POST['email']
        data['email'] = email
        if email_verification(email):
            try:
                Subscriber.objects.create(email=email)
                data['msg'] = ' is now registered successfully with us'
                data['status'] = 0
            except IntegrityError:
                data['msg'] = ' is already registered with us'
            except:
                data['status'] = 1
                data['msg'] = 'There seems to be an issue on our side. Please retry.'
            return JsonResponse(data)

        data['msg'] = ' is not a valid email'
        return JsonResponse(data)
    return HttpResponseBadRequest


@method_decorator(require_http_methods(['GET']), name='dispatch')
class FeaturedPostListView(ListView):
    """Returns a list view of featured posts."""

    template_name = 'Blog/post_list_featured.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        return published_posts().filter(featured=True)

    def get_context_data(self, **kwargs):
        context = super(FeaturedPostListView, self).get_context_data(**kwargs)
        context['meta'] = Meta(title='Featured Articles | HackAdda',
                               description='Read featured articles on HackAdda',
                               keywords=meta_home.keywords + ['featured'])
        return context


@method_decorator(require_http_methods(['GET']), name='dispatch')
class AuthorPostListView(ListView):
    # model = Post
    template_name = 'Blog/author_posts.html'   # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return published_posts().filter(author=user)

    def get_context_data(self, **kwargs):
        context = super(AuthorPostListView, self).get_context_data(**kwargs)
        context['author'] = get_object_or_404(User,
                                              username=self.kwargs.get(
                                                  'username')
                                              )
        context['meta'] = Meta(title=f'{context["author"].get_full_name().title()} | HackAdda',
                               description=f'Articles authored by {context["author"].get_full_name()}',
                               og_author=f'{context["author"].get_full_name()}',
                               keywords=meta_home.keywords)
        context['profile'] = context['author'].profile
        # print("Full name:",(get_object_or_404(User, pk=context['profile'].user_id).get_full_name()))
        return context


@method_decorator(require_http_methods(['GET']), name='dispatch')
@method_decorator(group(group_name='editor'), name='dispatch')
class UserPostListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Post
    template_name = 'Blog/user_posts.html'   # <app>/<model>_<viewtype>.html
    queryset = Post.objects.all()
    context_object_name = 'posts'
    paginate_by = 5

    def test_func(self):
        """Check if the logged in user is viewing their post"""
        return self.request.user.username == self.kwargs.get('username')

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user)
        tab = self.kwargs.get('tab', 'draft')

        if tab == 'queued':
            return self.queryset.filter(author=user, state=0).order_by('-date_created')
        elif tab == 'published':
            return self.queryset.filter(author=user, state=1).order_by('-date_published')
        else:  # for draft
            return self.queryset.filter(author=user, state=-1).order_by('-date_created')

    def get_context_data(self, **kwargs):
        context = super(UserPostListView, self).get_context_data(**kwargs)

        user = get_object_or_404(User, username=self.request.user)
        name = user.get_full_name()
        context['meta'] = Meta(title=f'{name} | HackAdda',
                               description=f'Articles authored by {name}',
                               og_author=f'{name}',
                               keywords=meta_home.keywords)
        return context


@method_decorator(require_http_methods(['GET']), name='dispatch')
class UserPostBookmark(LoginRequiredMixin, ListView):
    model = User
    context_object_name = 'posts'
    template_name = 'Blog/user_bookmarks.html'
    paginate_by = 5
    # queryset = User.objects.get_bookmarked_posts

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        if user == self.request.user:
            return user.profile.bookmarked_posts.order_by('-date_published')
        ### Return HTTP Error: "You should be logged in as the user" ###
        raise Http404(
            f'You should be signed in as {user} to view this page')

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)  # TODO
        context['profile'] = self.request.user.profile
        return context


@method_decorator(require_http_methods(['GET']), name='dispatch')
class PostDetailView(HitCountDetailView, DetailView):
    queryset = published_posts()
    context_object_name = 'post'
    count_hit = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meta'] = self.get_object().as_meta(self.request)
        if self.request.user.is_authenticated:
            context['profile'] = self.request.user.profile
        return context


@require_http_methods(['POST'])
def get_recommended_posts(request):
    """
    Condition:
        Works only for requests which are POST and AJAX.

    Args:
        post: the object whose recommended posts are request
        top_n: No. of recommended articles required

    Returns:
        Currently this function just returns the latest {top_n} posts (excluding the requesting post).

    TODO:
        Improve this function for a better user experience
    """
    if request.method == 'POST' and request.is_ajax:
        try:
            data = json.loads(request.POST.get('data'))
            slug = data['slug']
            top_n = int(data['top_n'])

        except Exception as _:
            return HttpResponseBadRequest(
                'Wrong Request Format for post request')

        template_name = 'post_latest_home.html'
        context = {}
        # Exclude the current post
        context['posts'] = published_posts().exclude(slug=slug)[:top_n]
        context['recommend'] = True
        return render(request, template_name, context)


@method_decorator(require_http_methods(['GET', 'POST']), name='dispatch')
@method_decorator(group(group_name='editor'), name='dispatch')
class PostCreateView(CreateView):
    model = Post
    fields = ['title', 'content', 'image', 'tags', 'category']

    def form_valid(self, form):
        form.instance.author = self.request.user
        if self.request.method == 'POST':
            form.instance.state = -1
            messages.success(
                self.request, 'Your article has been saved.')
        else:
            return HttpResponseBadRequest('Wrong request method')
        return super().form_valid(form)

    def get_success_url(self):
        """Since there's no absolute url in the model, this function provides a redirect on form success."""

        if 'draft' in self.request.POST:  # draft option was selected
            return reverse_lazy('Blog:draft-post-update', kwargs={'slug': self.object.slug})
        elif 'preview' in self.request.POST:
            return reverse_lazy('Blog:post-preview', kwargs={'slug': self.object.slug})
        else:
            return HttpResponseBadRequest('Wrong request!!!')


@method_decorator(require_http_methods(['GET', 'POST']), name='dispatch')
class DraftPostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'image', 'tags', 'category']

    def form_valid(self, form):
        # print("------->", 'form_valid')
        """
        Checks whether the user logged in is the one updating the post.
        Checks whether the user is authorised to update the article(only members of the group editors are allowed)
        It then reverses the published state so that admin's approval is required before publishing the updated post.
        """
        post = self.get_object()
        if self.request.user == post.author:
            messages.success(
                self.request, 'Your article has been saved.')
        else:
            messages.warning(
                self.request, 'You are not allowed to update this post.')
            return redirect('Blog:home')
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        """ensuring the author themselves is updating the post"""
        post = self.get_object()

        if self.request.user == post.author:
            return True
        raise PermissionDenied('You are not allowed to update this request')

    def get_success_url(self):
        """Since there's no absolute url in the model, this function provides a redirect on form success."""

        if 'draft' in self.request.POST:  # draft option was selected
            return reverse_lazy('Blog:draft-post-update', kwargs={'slug': self.object.slug})
        elif 'preview' in self.request.POST:
            return reverse_lazy('Blog:post-preview', kwargs={'slug': self.object.slug})
        else:
            return HttpResponseBadRequest('Wrong request!!!')


@method_decorator(require_http_methods(['GET', 'POST']), name='dispatch')
@method_decorator(group(group_name='editor'), name='dispatch')
class PostUpdateView(UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'image', 'tags', 'category']

    def form_valid(self, form):
        # print("------->", 'form_valid')
        """
        Checks whether the user logged in is the one updating the post.
        Checks whether the user is authorised to update the article(only members of the group editors are allowed)
        It then reverses the published state so that admin's approval is required before publishing the updated post.
        """
        post = self.get_object()
        if self.request.user == post.author:
            # Currently we can't keep more than 1 version of a Post
            # Hence when the preview option is selected, the state is changed to draft, and the post is unpublished
            # I(Abhyudai), currently expect the author to make review the changes soon in the next view and queue(editor) or publish them(superuser)
            # I know this is a dangerous.

            # if publish option is choosen
            if 'publish' in self.request.POST:
                # publish for superuser and queued for others
                if self.request.user.is_superuser:
                    form.instance.state = 1  # state -> published
                    messages.success(
                        self.request, 'Your article has been published.')
                else:
                    form.instance.state = 0  # state -> queued
                    messages.success(
                        self.request, 'Your article has been submitted for approval.')
            # otherwise set the state to draft
            else:
                form.instance.state = -1
        else:
            messages.warning(
                self.request, 'You are not allowed to update this post.')
            return redirect('Blog:home')

        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        """ensuring the author themselves is updating the post"""
        post = self.get_object()
        if self.request.user == post.author:
            return True
        raise PermissionDenied('You are not allowed to update this request')

    def get_success_url(self):
        """Since there's no absolute url in the model, this function provides a redirect on form success."""
        if 'publish' in self.request.POST:
            return reverse_lazy('Blog:home')
        elif 'preview' or 'draft' in self.request.POST:  # for both preview and draft, show preview
            return reverse_lazy('Blog:post-preview', kwargs={'slug': self.object.slug})
        else:
            return HttpResponseBadRequest('Wrong request!!!')


@method_decorator(require_http_methods(['GET', 'POST']), name='dispatch')
@method_decorator(group(group_name='editor'), name='dispatch')
class PostDeleteView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    fields = ['title', 'content', 'image', 'tags', 'category']
    success_url = reverse_lazy('Blog:home')
    success_message = "Post %(title)s was removed successfully"

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post has been deleted successfully!!!')
        return super().form_valid(form)

    def test_func(self):
        """ensuring the author itself is deleting the post."""
        post = self.get_object()
        if self.request.user == post.author:
            return True
        raise PermissionDenied('You are not allowed to update this request')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super().delete(request, *args, **kwargs)


@require_http_methods(['GET'])
def about(request):
    context = {}
    template_name = 'Blog/about.html'
    context['meta'] = Meta(title=f'About | HackAdda',
                           description=f'A glance at the stuff HackAdda offers',
                           keywords=meta_home.keywords)
    return render(request, template_name, context)


@group(group_name='editor')
@require_http_methods(['GET', 'POST'])
def preview(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == 'POST':
        """Submit post for review"""
        if request.user == post.author or request.user.is_superuser:
            if request.user.is_superuser:  # publish directly for superuser
                post.state = 1  # state -> published
                messages.success(
                    request, f'The article {post.title} has been published')
            else:
                post.state = 0  # state -> queued
                messages.success(
                    request, f'Your article {post.title} has been submitted for approval.')

            post.save()
        else:
            messages.warning(
                request, 'You are not allowed to update this post.')
        return redirect('Blog:home')
        # return reverse('Blog:my-posts', kwargs={'username': request.user, 'tab': 'drafts'})
    else:
        template_name = 'Blog/post_preview.html'
        return render(request, template_name, {'post': post})


@require_http_methods(['POST'])
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
    if request.method == 'POST' and request.is_ajax():
        data = {'message': '', 'status': 1}
        if request.user.is_authenticated:
            # print('POST request for bookmark made')
            slug = json.loads(request.body.decode('utf-8'))['data']
            pk = Post.objects.get(slug=slug).id
            b_post = Profile.objects.filter(
                user=request.user, bookmarked_posts=pk)
            # print(b_post)
            if not b_post:
                request.user.profile.bookmarked_posts.add(pk)
                data['message'] = 'Post bookmarked'
                data['status'] = 0
                # messages.success(request, 'Post bookmarked')
            else:
                request.user.profile.bookmarked_posts.remove(pk)
                data['message'] = 'Post removed from bookmarks'
                # messages.warning(request, 'Post already bookmarked')
            # print (data)
            return JsonResponse(data)

        # redirect with a message
        data['status'] = -1
        messages.info(
            request, 'You need to be logged in to bookmark a post')
        return JsonResponse(data)


@method_decorator(require_http_methods(['GET']), name='dispatch')
class TaggedPostListView(ListView):
    # model = Post
    template_name = 'Blog/post_tagged.html'   # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'

    def get_queryset(self):
        post_list = published_posts().filter(
            tags__contains=self.kwargs.get('tag').lower())
        if post_list:
            return post_list
        raise Http404('Tag not present')

    ordering = ['-date_published']
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = self.kwargs.get('tag').lower()
        context['meta'] = Meta(title=f'{tag.title()} | HackAdda',
                               description=f'Read articles with the tag {tag} on Hackadda',
                               keywords=meta_home.keywords + [tag])
        context['tag'] = tag
        return context


@require_http_methods(['GET', 'POST'])
def get_latest_posts(request, **kwargs):
    if request.method == 'POST' and request.is_ajax():
        template_name = 'post_title.html'
        # print('reached here:',type(json.loads(request.POST.get('data'))['num']))
        try:
            top_n = int(json.loads(request.POST.get('data'))['top_n'])
        except Exception as e:
            return HttpResponseBadRequest(
                'Wrong Request Format for post request')
        posts = published_posts()[:top_n]
        return render(request, template_name, {'posts': posts})

    elif request.method == 'GET':
        template_name = 'Blog/post_list_latest.html'
        paginate_by = 5
        posts = published_posts()
        kwargs['posts'] = paginate_util(request, posts, paginate_by, kwargs)
        kwargs['meta'] = Meta(title=f'Latest Articles| HackAdda',
                              description=f'Read latest articles on HackAdda',
                              keywords=meta_home.keywords + ['latest'])
        return render(request, template_name, kwargs)


@require_http_methods(['GET', 'POST'])
def get_tags(request):
    """
    1. Get request is used for top tags(mostly used)
    2. Post request is used for displaying the top_n tags in the sidebar
    """
    context = {}
    template_name = 'all_tags.html'
    flag = 0
    if request.method == 'POST' and request.is_ajax():
        template_name = 'tags.html'
        try:
            top_n = int(json.loads(request.POST.get('data'))['top_n'])
        except Exception as _:
            return HttpResponseBadRequest("Wrong Request Format")
        finally:
            flag = 1    # Tells whether post request was executed or get
            # For showing option of view more on sidebar
            context['ajax'] = True

    tags_list = [post.get_tags_list()
                 for post in published_posts()]
    if flag:    # for post request
        top_tags = Counter(
            [item for outer in tags_list for item in outer]).most_common(top_n)
    else:   # for get request
        top_tags = Counter(
            [item for outer in tags_list for item in outer]).most_common()

    top_tags_list = {tag: count for (tag, count) in top_tags}

    context['tags'] = top_tags_list

    # Tag clouds will be probably implemented in a better way
    # in a future release.
    # context['tags'] = get_font_cloud(top_tags_list)
    context['meta'] = Meta(title=f'Tags | HackAdda',
                           description=f'List of all Tags on HackAdda',
                           keywords=meta_home.keywords + list(top_tags_list.keys()))
    return render(request, template_name, context)


@method_decorator(require_http_methods(['GET']), name='dispatch')
class CategoryPostListView(ListView):
    # model = Post
    template_name = 'Blog/post_list_category.html'   # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'

    def get_queryset(self):
        post_list = published_posts().filter(
            category__slug=self.kwargs.get('slug').lower())
        if post_list:
            return post_list
        raise Http404('Category not present')

    ordering = ['-date_published']
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        category = get_object_or_404(Category, slug=slug)

        context['meta'] = Meta(title=f'{str(category).title()} | HackAdda',
                               description=f'Read articles of the category {category} from HackAdda',
                               keywords=meta_home.keywords + [category])
        context['category'] = category
        return context


@require_http_methods(['GET'])
def get_timewise_list(request, *args, **kwargs):

    template_name = 'Blog/post_list_time.html'
    paginate_by = 5

    if request.method == 'GET':
        dummy = datetime.now()  # to use formatting on template layer.
        kwargs = {k: int(v) if v is not None else v for k, v in kwargs.items()}
        dummy = dummy.replace(year=kwargs['year'])
        flag_day, flag_month = [1, 1]
        if kwargs['day'] is None:
            if kwargs['month'] is None:
                # both day and month are dummy values
                flag_day, flag_month = [0, 0]
            else:
                # month isn't dummy, day is dummy.
                flag_day, flag_month = [0, 1]
                dummy = dummy.replace(month=kwargs['month'])
        else:
            dummy = datetime(**kwargs)

        args_dict = {}
        args_dict['date_published__year'] = kwargs['year']
        if flag_day:
            args_dict['date_published__day'] = kwargs['day']
        if flag_month:
            args_dict['date_published__month'] = kwargs['month']

        posts = published_posts().filter(**args_dict)

        kwargs['date'], kwargs['flag_day'], kwargs['flag_month'] = dummy, flag_day, flag_month
        kwargs['posts'] = paginate_util(request, posts, paginate_by, kwargs)
        kwargs['meta'] = meta_home
        return render(request, template_name, kwargs)


@require_http_methods(['GET', 'POST'])
def get_category(request):
    """
    Get categories(foreign key) present in Blog
    1. For get request, all categories are shown in a page.
    2. For post request, top_n categories are shown in the sidebar.
    """
    context = {}
    flag = 0
    template_name = 'all_categories.html'

    if request.method == 'POST' and request.is_ajax():
        template_name = 'Blog/categories.html'
        try:
            top_n = int(json.loads(request.POST.get('data'))['top_n'])
        except Exception as _:
            return HttpResponseBadRequest("Wrong Request Format")
        finally:
            flag = 1
            context['ajax'] = True

    categories = Category.objects.filter(
        post__in=published_posts())

    if flag:  # POST request
        top_categories = Counter(categories).most_common(top_n)
    else:
        top_categories = Counter(categories).most_common()

    top_categories_list = {
        category: count for (category, count) in top_categories}
    top_categories_list_str = [str(category)
                               for category in top_categories_list]
    context['categories'] = top_categories_list
    context['meta'] = Meta(title=f'Categories | HackAdda',
                           description=f'List of all Categories on HackAdda',
                           keywords=meta_home.keywords + top_categories_list_str)

    return render(request, template_name, context)


@require_http_methods(['POST'])
def get_trending_posts(request):
    """Returns top_n trending post for a given time period for POST requests in AJAX format."""

    if request.method == 'POST' and request.is_ajax():
        template_name = 'post_title.html'
        # start_time = time.time()
        try:
            top_n = int(json.loads(request.POST.get('data'))['top_n'])
            # top_n = int(request.GET.get('top_n'))
        except Exception as _:
            return HttpResponseBadRequest("Wrong Request Format")
        posts = published_posts()
        trending_posts = trending(posts, top_n=top_n)
        # print('\nTotal time taken:', time.time() - start_time)
        # print('Trending posts:', trending_posts)
        return render(request, template_name, {'posts': trending_posts, 'meta': meta_home})


class LatestPostRSSFeed(Feed):
    title = 'Latest posts from HackAdda'
    link = ''
    description = meta_home.description

    def items(self, top_n=5):
        return published_posts()[:top_n]

    def item_title(self, item):
        return item.title

    def item_author_name(self, item):
        return item.author.get_full_name()

    def item_description(self, item):
        return item._get_meta_description()

    def item_link(self, item):
        return item.get_detail_url()
