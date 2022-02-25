from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post
import db_func as db
from pathlib import Path

database = str(Path.cwd()) + "/protected.db"
client_ids = []
db_conn = db.create_connection(database)
client = db.select_client(db_conn)

def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog_app/home.html', context)

def dashboard(request):

    dashboard = []

    for key, val in client.items():
        dashboard.append((val[0], val[1], val[2], val[3], val[4]))
        client_ids.append(key)
    dashboard = sorted(dashboard, key = lambda item: item[2], reverse=True)
    dashboard = [(idx+1, item[0], item[1], item[2], item[3], item[4]) for idx, item in enumerate(dashboard)]
    context = {
        'dashboard': dashboard
    }
    return render(request, 'blog_app/dashboard.html', context)


def UserDetailView(request, key):

    db_conn = db.create_connection(database)
    details = db.select_comms(db_conn, key)
    sent = details[key][0]
    recv = details[key][1]
    time = details[key][2]

    context = {
        'sent': sent,
        'recv': recv,
        'time': time
    }
    return render(request, 'blog_app/userdetails.html', context)



class PostListView(ListView):
    model = Post
    template_name = 'blog_app/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = 'blog_app/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

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
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, 'blog_app/about.html', {'title': 'About'})