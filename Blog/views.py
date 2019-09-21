from django.shortcuts import render
from django.views.generic import (ListView,
                                    DetailView,
                                    CreateView,
                                    UpdateView,
                                    DeleteView
                                    )
from .models import Post
from Users.models import Profile
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import JsonResponse
import json

# Create your views here.
def home(request):
    context = {
        'posts':Post.objects.filter(publish=True)
    }
    return render(request, 'Blog/home.html',context)

class PostListView(ListView):
    # model = Post
    template_name = 'Blog/home.html'   # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    queryset = Post.objects.filter(publish=True)
    ordering = ['-date_posted']
    paginate_by = 5
        


class UserPostListView(ListView):
    # model = Post
    template_name = 'Blog/user_posts.html'   # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    queryset = Post.objects.filter(publish=True)
    # ordering = ['-date_posted']
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super(UserPostListView, self).get_context_data(**kwargs)
        context['author'] = get_object_or_404(User,
                                                username=self.kwargs.get('username')
                                                )
        context['profile'] = get_object_or_404(Profile,
                                                user=get_object_or_404(
                                                    User,
                                                    username=self.kwargs.get('username')
                                                    ))
        # print("Full name:",(get_object_or_404(User, pk=context['profile'].user_id).get_full_name()))
        return context



class PostDetailView(DetailView):
    queryset = Post.objects.filter(publish=True)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'short_des', 'content', 'tags']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'short_des', 'content', 'tags']

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
