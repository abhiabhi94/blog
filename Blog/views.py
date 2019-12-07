from django.shortcuts import render
from django.views.generic import (ListView,
                                  DetailView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView
                                  )
from .models import Post
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from Users.models import Profile
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.models import User
from django.http import JsonResponse, Http404
from django.urls import reverse_lazy
from collections import Counter
from meta.views import Meta
import json
from datetime import datetime


'''
Use the name posts for backend purposes.
Use the name articles for frontend purposes.
'''


def published_posts(order='-date_posted'):
    '''
    TODO: support multiple filters.
    returns a list of published posts. 
    if no order is given, the posts are ordered by their post date.
    '''
    return Post.objects.filter(publish=True).order_by(order)


global meta_home
meta_home = Meta(title='StayCurious Blog | Nurturing curiosity in every mind.',
                 description='Articles that encourage coding, robotics through STEM education',
                 keywords=['robotics, coding, STEM, STEAM, education, blog, tinker, kids, StayCurious, curiousity'])


class HomeView(ListView):
    '''Return featured, latest, and categories wise articles for the front-page'''

    template_name = 'Blog/home.html'   # <app>/<model>_<viewtype>.html
    # context_object_name = 'posts'
    # paginate_by = 5
    # posts_unique = {}

    def __init__(self):
        self.NO_FEATURED_POSTS = 3
        self.NO_LATEST_POSTS = 5
        self.NO_CATEGORY_POSTS = 2
        super().__init__()

    def get_queryset(self):
        return published_posts()

    def remove_duplicates(self, current, unique, top_n):
        '''
        Returns unique posts in current after removing duplicate objects from it.
        Set difference is calculated here as a part of list comphrehension in order to maintain order.
        '''
        unique = set(unique)
        print('unique>>>', unique, '\n')
        current_unique = [i for i in current if i not in unique][:top_n]
        print('current-unique', current_unique, '\n')
        unique = unique.union(set(current_unique))
        # # Finds union of both lists (current_unique)
        # union = current_unique + [i for i in unique if i in current_unique]
        print('unique after union>>>', unique, '\n')
        return current_unique, unique

    def get_featured_posts(self):
        '''Returns top_n featured posts
        where top_n is self.NO_FEATURED_POSTS
        '''
        top_n = self.NO_FEATURED_POSTS

        return published_posts().filter(featured=True)[:top_n]

    def get_latest_posts(self):
        '''
        Returns top_n latest_posts
        +self.NO_LATEST_POSTS latest posts for 
        +self.NO_FEATURED_POSTS is for checking duplicacy with featured articles
        '''
        top_n = self.NO_LATEST_POSTS + self.NO_FEATURED_POSTS

        return published_posts()[:top_n]

    def get_category_posts(self, category, index):
        '''
        Returns top_n posts under a certain category.
        for top_n = +self.NO_FEATURED_POSTS is for featured articles
                    +self.NO_LATEST_POSTS is for latest articles
                    +self.NO_CATEGORY_POSTS * index is for extra articles in case of duplicacy with the above categories.
        '''

        top_n = self.NO_FEATURED_POSTS + self.NO_LATEST_POSTS + \
            self.NO_CATEGORY_POSTS * (index)
        return published_posts().filter(category__name=category)[:top_n]

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['meta'] = meta_home
        context['featured_posts'] = list(self.get_featured_posts())
        posts_unique = context['featured_posts']

        latest_posts = list(self.get_latest_posts())
        context['latest_posts'], posts_unique = self.remove_duplicates(
            latest_posts, posts_unique, self.NO_LATEST_POSTS)

        categories = ['science', 'technology']
        # context['categories'] = categories

        category_result = {}
        for index, category in enumerate(categories):
            category_posts = list(self.get_category_posts(category, index))
            category_posts_unique, posts_unique = self.remove_duplicates(
                category_posts, posts_unique, self.NO_CATEGORY_POSTS)
            # context['category_posts'].append(
            #     context['category_' + category + '_posts'])
            category_result[category] = category_posts_unique
        context['category'] = category_result
        if self.request.user.is_authenticated:
            context['profile'] = self.request.user.profile
        print("Featured>>>", context['featured_posts'])
        print("Latest>>>", context['latest_posts'])
        print("Categories>>>", context['category'])

        return context


class FeaturedPostListView(ListView):
    '''
    Returns a list view of featured posts
    '''
    template_name = 'post_list_generic.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        return published_posts().filter(featured=True)


class PostListView(ListView):
    # model = Post
    template_name = 'Blog/home.html'   # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        return published_posts()

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        context['meta'] = meta_home
        if self.request.user.is_authenticated:
            context['profile'] = self.request.user.profile
        return context


class UserPostListView(ListView):
    # model = Post
    template_name = 'Blog/user_posts.html'   # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return published_posts().filter(author=user)

    def get_context_data(self, **kwargs):
        context = super(UserPostListView, self).get_context_data(**kwargs)
        context['author'] = get_object_or_404(User,
                                              username=self.kwargs.get(
                                                  'username')
                                              )
        context['meta'] = Meta(title=f'Posts by {context["author"].get_full_name()}',
                               description=f'Posts authored by {context["author"].get_full_name()}',
                               keywords=meta_home.keywords)
        context['profile'] = context['author'].profile
        # print("Full name:",(get_object_or_404(User, pk=context['profile'].user_id).get_full_name()))
        return context


class UserPostBookmark(LoginRequiredMixin, ListView):
    model = User
    context_object_name = 'posts'
    template_name = 'Blog/user_bookmarks.html'
    paginate_by = 5
    # queryset = User.objects.get_bookmarked_posts

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        if user == self.request.user:
            #     # print(dir(user.profile.bookmarked_posts.values_list()))
            #     # print(user.profile.bookmarked_posts.all())
            #     print(self.request.user.profile)
            return user.profile.bookmarked_posts.all()
        ### Return HTTP Error: "You should be logged in as the user" ###
        raise Http404(
            "You should be signed in as %s to view this page" % (user))

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['profile'] = self.request.user.profile
        return context


class PostDetailView(DetailView):
    queryset = published_posts()
    # context_object_name = 'object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['object'].tags = context['object'].tags.split()
        context['meta'] = self.get_object().as_meta(self.request)
        if self.request.user.is_authenticated:
            context['profile'] = self.request.user.profile
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'thumbnail', 'tags', 'category']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'thumbnail', 'tags', 'category']

    def form_valid(self, form):
        # print("------->", 'form_valid')
        '''
        Checks whether the user logged in is the one updating the post.
        It then reverses the published state so that admin's approval is required before publishing the updated post.
        '''
        post = self.get_object()
        if self.request.user == post.author:
            messages.success(
                self.request, 'Your post has been submitted for approval')
        else:
            messages.warning(
                self.request, 'Only posts written by you can be updated')
            return redirect('Blog:home')
        form.instance.author = self.request.user
        form.instance.publish = False
        return super().form_valid(form)

    def test_func(self):
        '''ensuring the author themselves is updating the post'''
        # print("*************", 'test_func')
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

    # def post(self, *args, **kwargs):
    #     post = self.get_object()
    #     if self.request.user == post.author:
    #         print('inside post request')
    #         messages.success(
    #             self.request, 'Your post has been submitted for approval')
    #         return redirect('Blog:home')
    #     else:
    #         messages.warning(
    #             self.request, 'Only posts written by you can be updated')
    #         return redirect('Blog:home')


class PostDeleteView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    fields = fields = ['title', 'content', 'thumbnail', 'tags', 'category']
    success_url = '/blog'  # redirected path
    success_url = reverse_lazy('Blog:home')
    success_message = "Post %(title)s was removed successfully"

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post has been deleted successfully!!!')
        return super().form_valid(form)

    def test_func(self):
        '''ensuring the author itself is deleting the post.'''
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super().delete(request, *args, **kwargs)


def about(request):
    return render(request, 'Blog/about.html', {'title': 'About'})


@login_required
def preview(request, year, month, day, slug):
    post = Post.objects.get(slug=slug)
    # print(post.author)
    # if request.user == post.author:
    #     if request.method == 'POST':
    #         # print ('inside post request')
    #         messages.success(
    #             request, 'Your post has been submitted for approval')
    #         return redirect('Blog:home')
    # else:
    #     messages.warning(request, 'Only posts written by you can be previewed')
    #     return redirect('Blog:home')
    return render(request, 'Blog/post_preview.html', {'post': post})


@login_required
def bookmark_post(request):
    if request.method == 'POST' and request.is_ajax():
        data = {'message': '', 'status': 1}
        # print('POST request for bookmark made')
        slug = json.loads(request.body.decode('utf-8'))['data']
        pk = Post.objects.get(slug=slug).id
        b_post = Profile.objects.filter(user=request.user, bookmarked_posts=pk)
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

    else:
        return redirect('Blog:home')


class TaggedPostListView(ListView):
    # model = Post
    template_name = 'Blog/post_tagged.html'   # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'

    def get_queryset(self):
        post_list = published_posts().filter(tags__contains=self.kwargs.get('tag'))
        if post_list:
            return post_list
        raise Http404('Tag not present')

    ordering = ['-date_posted']
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = self.kwargs.get('tag')
        context['meta'] = Meta(title=f'Posts tagged with {tag}',
                               description=f'Read posts with the tag {tag} from StayCurious',
                               keywords=meta_home.keywords + [tag])
        return context


def get_latest_posts(request, **kwargs):
    if request.method == 'POST':
        template_name = 'post_title.html'
        # print('reached here:',type(json.loads(request.POST.get('data'))['num']))
        try:
            num = int(json.loads(request.POST.get('data'))['num'])
        except Exception as e:
            raise Http404('Wrong Request Format for post request')
        posts = published_posts()[:num]
        return render(request, template_name, {'posts': posts})

    elif request.method == 'GET':
        template_name = 'post_list_generic.html'
        paginate_by = 5
        posts = published_posts()
        kwargs['posts'] = paginate_util(request, posts, paginate_by, kwargs)
        return render(request, template_name, kwargs)

    raise Http404('Wrong Request format')


def get_tags(request):  # used in right sidebar
    if request.method == 'POST':
        template_name = 'tags.html'
        tags_list = [post.get_tags_list()
                     for post in published_posts()]
        tags_list = list({item for outer in tags_list for item in outer})
        # top_tags_list =  {tag:count for (tag, count) in top_tags}

        # print(top_tags_list)
        return render(request, template_name, {'tags': tags_list})

    raise Http404("Wrong Request Format")


def get_top_tags(request):  # used in right side bar above all tags.
    if request.method == 'POST':
        template_name = 'tags.html'
        try:
            num = int(json.loads(request.POST.get('data'))['num'])
        except Exception as e:
            raise Http404("Wrong Request Format")
        tags_list = [post.get_tags_list()
                     for post in published_posts()]
        top_tags = Counter(
            [item for outer in tags_list for item in outer]).most_common(num)
        top_tags_list = {tag: count for (tag, count) in top_tags}
        return render(request, template_name, {'tags': top_tags_list, 'html': True})

    raise Http404("Wrong Request Format")


class CategoryPostListView(ListView):
    # model = Post
    template_name = 'Blog/post_list_category.html'   # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'

    def get_queryset(self):
        post_list = published_posts().filter(category__name=self.kwargs.get('category'))
        if post_list:
            return post_list
        raise Http404('Category not present')

    ordering = ['-date_posted']
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.kwargs.get('category')
        context['meta'] = Meta(title=f'Posts tagged with {category}',
                               description=f'Read posts with the category {category} from HackAdda',
                               keywords=meta_home.keywords + [category])
        return context


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
        args_dict['date_posted__year'] = kwargs['year']
        if flag_day:
            args_dict['date_posted__day'] = kwargs['day']
        if flag_month:
            args_dict['date_posted__month'] = kwargs['month']

        posts = published_posts().filter(**args_dict)

        kwargs['date'], kwargs['flag_day'], kwargs['flag_month'] = dummy, flag_day, flag_month
        kwargs['posts'] = paginate_util(request, posts, paginate_by, kwargs)
        return render(request, template_name, kwargs)

    raise Http404("Wrong Request Format")


def paginate_util(request, objects, paginate_by, kwargs):
    # Show {paginate_by} objects per page
    paginator = Paginator(objects, paginate_by)
    page = request.GET.get('page')
    objects = paginator.get_page(page)
    if paginator.num_pages > 1:  # no point in paginating if there is only one page.
        kwargs['is_paginated'] = True
    kwargs['page_obj'] = objects
    return objects
