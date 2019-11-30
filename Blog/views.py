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

global meta_home
meta_home = Meta(title='StayCurious Blog | Nurturing curiosity in every mind.',
                 description='Articles that encourage coding, robotics through STEM education',
                 keywords=['robotics, coding, STEM, STEAM, education, blog, tinker, kids, StayCurious, curiousity'])


class PostListView(ListView):
    # model = Post
    template_name = 'Blog/home.html'   # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        return Post.objects.filter(publish=True).order_by('-date_posted')

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
    # queryset = Post.objects.filter(publish=True)
    # ordering = ['-date_posted']
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        # print(Post.objects.filter(author=user).order_by('-date_posted'))
        return Post.objects.filter(author=user, publish=True).order_by('-date_posted')

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
    queryset = Post.objects.filter(publish=True)
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
    fields = ['title', 'content', 'tags']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'thumbnail', 'tags', 'category']
    def form_valid(self, form):
        print("------->", 'form_valid')
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        print("*************", 'test_func')
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

    def post(self, *args, **kwargs):
        post = self.get_object()
        post.publish = False
        if self.request.user == post.author:
            # print ('inside post request')
            messages.success(
                self.request, 'Your post has been submitted for approval')
            return redirect('Blog:home')
        else:
            messages.warning(self.request, 'Only posts written by you can be previewed')
            return redirect('Blog:home')        

class PostDeleteView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    fields = ['title', 'content', 'tags']
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


# def tagged_post(request, tag):
#     result = Post.objects.filter(string__contains=tag)
#     return render(request, 'Blog/about.html', {'title':'About'})

class TaggedPostListView(ListView):
    # model = Post
    template_name = 'Blog/post_tagged.html'   # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    # queryset = Post.objects.filter(tags__contains=self.kwargs.get('tag'))

    def get_queryset(self):
        post_list = Post.objects.filter(
            tags__contains=self.kwargs.get('tag'), publish=True).order_by('-date_posted')
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


def get_latest_posts(request):
    if request.method == 'POST':
        template_name = 'post_title.html'
        # print('reached here:',type(json.loads(request.POST.get('data'))['num']))
        try:
            num = int(json.loads(request.POST.get('data'))['num'])
        except Exception as e:
            raise Http404("Wrong Request Format")
        posts = Post.objects.filter(
            publish=True).order_by('-date_posted')[:num]
        return render(request, template_name, {'posts': posts})

    raise Http404('Wrong Request format')


def get_tags(request):  # used in right sidebar
    if request.method == 'POST':
        template_name = 'tags.html'
        tags_list = [post.get_tags_list()
                     for post in Post.objects.filter(publish=True)]
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
                     for post in Post.objects.filter(publish=True)]
        top_tags = Counter(
            [item for outer in tags_list for item in outer]).most_common(num)
        top_tags_list = {tag: count for (tag, count) in top_tags}
        return render(request, template_name, {'tags': top_tags_list, 'html': True})

    raise Http404("Wrong Request Format")


class CategoryPostListView(ListView):
    # model = Post
    template_name = 'Blog/post_categorized.html'   # <app>/<model>_<viewtype>.html
    context_object_name = 'categories'
    # queryset = Post.objects.filter(tags__contains=self.kwargs.get('tag'))

    def get_queryset(self):
        post_list = Post.objects.filter(
            category__category_name=self.kwargs.get('category'), publish=True).order_by('-date_posted')
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

    template_name = 'Blog/time_list.html'
    paginate_by = 5

    if request.method == 'GET':
        dummy = datetime.now() # to use formatting on template layer.
        kwargs = {k:int(v) if v is not None else v for k,v in kwargs.items()}
        dummy.replace(year=kwargs['year'])
        flag_day, flag_month = [1,1]
        if kwargs['day'] is None:
            if kwargs['month'] is None:
                flag_day, flag_month = [0,0] # day, month    
            else:
                flag_day, flag_month = [0,1] # day, month
                dummy.replace(month=kwargs['month'])
        else:
            dummy = datetime(**kwargs)

        args_dict = {}
        args_dict['date_posted__year'] = kwargs['year']
        if flag_day:
            args_dict['date_posted__day'] = kwargs['day']
        if flag_month:
            args_dict['date_posted__month'] = kwargs['month']

        posts = Post.objects.filter(publish=True, **args_dict).order_by('-date_posted')        
        
        kwargs['date'], kwargs['flag_day'], kwargs['flag_month'] = dummy, flag_day, flag_month
        kwargs['posts'] = paginate_util(request, posts, paginate_by, kwargs)
        return render(request, template_name, kwargs)

    raise Http404("Wrong Request Format")    

def paginate_util(request, objects, paginate_by, kwargs):
    paginator = Paginator(objects, paginate_by) # Show 25 contacts per page
    page = request.GET.get('page')
    objects = paginator.get_page(page)        
    if paginator.num_pages>1: # no point in paginating if there is only one page.
        kwargs['is_paginated'] = True
    kwargs['page_obj'] = objects
    return objects    
