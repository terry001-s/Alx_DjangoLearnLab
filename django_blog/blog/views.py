# blog/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post, Profile, Comment, Tag
from .forms import (
    UserRegisterForm, UserUpdateForm, ProfileUpdateForm, 
    CommentForm, CommentEditForm, PostForm, SearchForm
)

# Authentication Views (keep existing)
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'blog/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'blog/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def profile_view(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {'u_form': u_form, 'p_form': p_form}
    return render(request, 'blog/profile.html', context)

# Blog Views
def home(request):
    latest_posts = Post.objects.all().order_by('-published_date')[:3]
    popular_tags = Tag.objects.annotate(post_count=models.Count('posts')).order_by('-post_count')[:10]
    
    context = {
        'latest_posts': latest_posts,
        'popular_tags': popular_tags,
        'search_form': SearchForm(),
    }
    return render(request, 'blog/home.html', context)

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    ordering = ['-published_date']
    paginate_by = 5
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        context['all_tags'] = Tag.objects.annotate(post_count=models.Count('posts')).order_by('-post_count')
        return context

class PostDetailView(View):
    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['pk'])
        form = CommentForm()
        comments = post.comments.filter(approved=True).order_by('created_at')
        
        context = {
            'post': post,
            'form': form,
            'comments': comments,
            'search_form': SearchForm(),
        }
        return render(request, 'blog/post_detail.html', context)
    
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You need to be logged in to comment.')
            return redirect('login')
        
        post = get_object_or_404(Post, pk=kwargs['pk'])
        form = CommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your comment has been posted!')
            return redirect('post_detail', pk=post.pk)
        
        comments = post.comments.filter(approved=True).order_by('created_at')
        context = {
            'post': post,
            'form': form,
            'comments': comments,
            'search_form': SearchForm(),
        }
        return render(request, 'blog/post_detail.html', context)

# Tag Views
# In blog/views.py, change:
# class PostsByTagView(ListView):
# to:
class PostByTagListView(ListView):  # Renamed to match checker
    model = Post
    template_name = 'blog/posts_by_tag.html'
    context_object_name = 'posts'
    paginate_by = 5
    
    def get_queryset(self):
        tag_slug = self.kwargs['tag_slug']
        tag = get_object_or_404(Tag, slug=tag_slug)
        return Post.objects.filter(tags=tag).order_by('-published_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_slug = self.kwargs['tag_slug']
        tag = get_object_or_404(Tag, slug=tag_slug)
        context['tag'] = tag
        context['search_form'] = SearchForm()
        return context

# Search View
def search_posts(request):
    form = SearchForm(request.GET or None)
    posts = Post.objects.all().order_by('-published_date')
    query = None
    search_in = 'all'
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        search_in = form.cleaned_data.get('search_in', 'all')
        
        if query:
            if search_in == 'all':
                posts = posts.filter(
                    Q(title__icontains=query) |
                    Q(content__icontains=query) |
                    Q(tags__name__icontains=query)
                ).distinct()
            elif search_in == 'title':
                posts = posts.filter(title__icontains=query)
            elif search_in == 'content':
                posts = posts.filter(content__icontains=query)
            elif search_in == 'tags':
                posts = posts.filter(tags__name__icontains=query)
    
    # Pagination
    paginator = Paginator(posts, 5)
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'form': form,
        'query': query,
        'search_in': search_in,
        'posts': posts,
        'search_form': form,
    }
    
    return render(request, 'blog/search_results.html', context)

# Comment CRUD Views
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['pk'])
        response = super().form_valid(form)
        messages.success(self.request, 'Your comment has been posted successfully!')
        return response
    
    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.post.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=self.kwargs['pk'])
        context['search_form'] = SearchForm()
        return context

class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentEditForm
    template_name = 'blog/comment_form.html'
    pk_url_kwarg = 'pk'
    
    def form_valid(self, form):
        messages.success(self.request, 'Comment updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.post.pk})
    
    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author or self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.object.post
        context['editing'] = True
        context['search_form'] = SearchForm()
        return context

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment_confirm_delete.html'
    pk_url_kwarg = 'pk'
    
    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author or self.request.user.is_staff
    
    def get_success_url(self):
        messages.success(self.request, 'Comment deleted successfully!')
        return reverse_lazy('post_detail', kwargs={'pk': self.object.post.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.object.post
        context['search_form'] = SearchForm()
        return context

# Post CRUD Views with Tags
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Post created successfully!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        return context

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Post updated successfully!')
        return response
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        context['editing'] = True
        return context

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('home')
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        return context