from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

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


class PostDetailView(DetailView):
    queryset = Post.objects.filter(publish=True)


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
    print(post.author)
    if request.user == post.author :    
        if request.method == 'POST':
            # print ('inside post request')
            messages.success(request, 'Your post has been submitted for approval')
            return redirect('Blog:home')
    else:
        messages.warning(request, 'Only posts written by you can be previewed')
        return redirect('Blog:home')
    return render(request, 'Blog/post_preview.html', {'post':post})
