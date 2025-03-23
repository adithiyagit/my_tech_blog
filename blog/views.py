from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic.edit import CreateView
from django.db.models import Q, Count
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Blog, BlogAuthor, Comment, Category, Tag, UserProfile

def index(request):
    """View function for home page of site."""
    # Get published blog posts
    blogs = Blog.objects.filter(status='published').order_by('-post_date')[:5]
    
    # Get popular authors
    popular_authors = BlogAuthor.objects.annotate(
        post_count=Count('blog')
    ).order_by('-post_count')[:3]
    
    # Get categories and tags
    categories = Category.objects.all()
    tags = Tag.objects.all()
    
    context = {
        'recent_posts': blogs,
        'popular_authors': popular_authors,
        'categories': categories,
        'tags': tags,
    }
    
    return render(request, 'blog/index.html', context)

class BlogListView(generic.ListView):
    model = Blog
    paginate_by = 5
    template_name = 'blog/blog_list.html'
    context_object_name = 'blog_list'
    
    def get_queryset(self):
        queryset = Blog.objects.all()  # Start with all blogs
        
        # Filter by status if the field exists
        try:
            queryset = queryset.filter(status='published')
        except:
            pass  # If status field doesn't exist yet, show all posts
            
        search_query = self.request.GET.get('search', '')
        category = self.request.GET.get('category', '')
        tag = self.request.GET.get('tag', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(author__user__username__icontains=search_query)
            )
        
        if category:
            queryset = queryset.filter(categories__slug=category)
        
        if tag:
            queryset = queryset.filter(tags__slug=tag)
        
        return queryset.order_by('-post_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['recent_posts'] = Blog.objects.filter(status='published')[:5]
        except:
            context['recent_posts'] = Blog.objects.all()[:5]
            
        context['popular_authors'] = BlogAuthor.objects.annotate(
            post_count=Count('blog')
        ).order_by('-post_count')[:5]
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        return context

class BloggerListView(generic.ListView):
    model = BlogAuthor
    template_name = 'blog/blogger_list.html'
    context_object_name = 'blogger_list'
    paginate_by = 12

    def get_queryset(self):
        return BlogAuthor.objects.annotate(
            post_count=Count('blog', filter=Q(blog__status='published'))
        ).order_by('-post_count')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Our Bloggers'
        return context

class BlogDetailView(generic.DetailView):
    model = Blog
    template_name = 'blog/blog_detail.html'
    
    def get_object(self):
        obj = super().get_object()
        obj.views += 1
        obj.save()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comment_set.filter(parent=None)
        context['related_posts'] = Blog.objects.filter(
            categories__in=self.object.categories.all()
        ).exclude(id=self.object.id)[:3]
        return context

class BloggerDetailView(generic.DetailView):
    model = BlogAuthor
    template_name = 'blog/blogger_detail.html'
    context_object_name = 'blogger'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_posts'] = Blog.objects.filter(status='published')[:5]
        context['popular_authors'] = BlogAuthor.objects.annotate(
            post_count=Count('blog')
        ).order_by('-post_count')[:5]
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        return context

@method_decorator(login_required, name='dispatch')
class BlogCommentCreate(CreateView):
    model = Comment
    fields = ['content', 'parent']
    template_name = 'blog/comment_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('blog-detail', kwargs={'slug': self.kwargs['slug']})

@login_required
def toggle_like(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    if request.user in blog.likes.all():
        blog.likes.remove(request.user)
        liked = False
    else:
        blog.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': blog.likes.count()})

@login_required
def add_comment(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    if request.method == 'POST':
        content = request.POST.get('content')
        parent_id = request.POST.get('parent')
        
        if content:
            comment = Comment(
                blog=blog,
                author=request.user,
                content=content
            )
            if parent_id:
                comment.parent = Comment.objects.get(id=parent_id)
            comment.save()
            
            return JsonResponse({
                'status': 'success',
                'comment_id': comment.id,
                'author': comment.author.username,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%B %d, %Y'),
                'likes': 0
            })
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def like_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'status': 'success',
        'liked': liked,
        'likes_count': comment.likes.count()
    })

@login_required
def like_blog(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    if request.user in blog.likes.all():
        blog.likes.remove(request.user)
        liked = False
    else:
        blog.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'status': 'success',
        'liked': liked,
        'likes_count': blog.likes.count()
    })

@login_required
def toggle_dark_mode(request):
    profile = request.user.userprofile
    profile.dark_mode = not profile.dark_mode
    profile.save()
    return JsonResponse({'dark_mode': profile.dark_mode})
