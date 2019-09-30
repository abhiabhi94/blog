from django.shortcuts import render
from django.views.generic import (ListView,
                                    DetailView,
                                    CreateView,
                                    UpdateView,
                                    DeleteView
                                    )
from .models import Post
from django.contrib.auth.models import User
from Users.models import Profile
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import JsonResponse, Http404
from collections import Counter
import json

# Create your views here.
# def home(request):
#     context = {
#         'posts':Post.objects.filter(publish=True)
#     }
#     return render(request, 'Blog/home.html',context)

class PostListView(ListView):
    # model = Post
    template_name = 'Blog/home.html'   # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        return Post.objects.filter(publish=True).order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['profile'] = self.request.user.profile
            # context['bookmarks'] = [post.id for post in self.request.user.profile.bookmarked_posts.all()]
        return context


class UserPostListView(ListView):
    # model = Post
    template_name = 'Blog/user_posts.html'   # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    queryset = Post.objects.filter(publish=True)
    # ordering = ['-date_posted']
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        # print(Post.objects.filter(author=user).order_by('-date_posted'))
        return Post.objects.filter(author=user).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super(UserPostListView, self).get_context_data(**kwargs)
        context['author'] = get_object_or_404(User,
                                                username=self.kwargs.get('username')
                                                )
        context['profile'] = context['author'].profile
        # print("Full name:",(get_object_or_404(User, pk=context['profile'].user_id).get_full_name()))
        return context

class UserPostBookmark(LoginRequiredMixin, ListView):
    model=User
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
        raise Http404("You should be signed in as bkjha to view this page")
    
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
    fields = ['title', 'content', 'tags']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    fields = ['title', 'content', 'tags']
    success_url = '/blog'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

def about(request):
    return render(request, 'Blog/about.html', {'title':'About'})

@login_required
def preview(request, slug):
    post = Post.objects.get(slug=slug)
    # print(post.author)
    if request.user == post.author :    
        if request.method == 'POST':
            # print ('inside post request')
            messages.success(request, 'Your post has been submitted for approval')
            return redirect('Blog:home')
    else:
        messages.warning(request, 'Only posts written by you can be previewed')
        return redirect('Blog:home')
    return render(request, 'Blog/post_preview.html', {'post':post})

@login_required
def bookmark_post(request):
    if request.method == 'POST' and request.is_ajax():
        data = {'message':'', 'status':1}
        print('POST request made')
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
        return context   

# def get_post_list(request):
#     num = request.GET.get('num')
#     print(Post.objects.filter(publish=True).orderby('-date_posted')[num])
#     return None

def get_tags(request):
        template_name = 'tags.html'
        tags_list = [post.get_tags_list()
                    for post in Post.objects.filter(publish=True)]
        tags_list = list({item for outer in tags_list for item in outer})
        # top_tags_list =  {tag:count for (tag, count) in top_tags}

        # print(top_tags_list)
        if request.method == 'GET':
            return render(request, template_name, {'tags': tags_list})
        elif request.method == 'POST':
            return JsonResponse(tags_list)

def get_top_tags(request):
    template_name = 'tags.html'
    if request.method == 'GET':
        try:
            top_n = int(request.GET.get('num'))
        except ValueError:
            raise Http404("Wrong Request Format")
        tags_list = [post.get_tags_list()
                    for post in Post.objects.filter(publish=True)]
        top_tags = Counter(
            [item for outer in tags_list for item in outer]).most_common(top_n)
        top_tags_list = {tag: count for (tag, count) in top_tags}
        if request.is_ajax():
            return render(request, template_name, {'tags': top_tags_list})
        else:
            return render(request, template_name, {'tags': top_tags_list, 'html':True})
