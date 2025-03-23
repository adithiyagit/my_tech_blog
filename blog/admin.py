from django.contrib import admin
from django.utils.html import format_html
from .models import Blog, BlogAuthor, Comment, Category, Tag, UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'dark_mode', 'avatar_preview')
    list_filter = ['dark_mode']
    search_fields = ('user__username',)
    
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="width: 30px; height: 30px; border-radius: 50%;" />', obj.avatar.url)
        return "No Avatar"
    avatar_preview.short_description = 'Avatar'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ['post_date']
    fields = ['author', 'content', 'post_date', 'likes']
    raw_id_fields = ['author']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['truncated_content', 'blog', 'author', 'post_date', 'like_count']
    list_filter = ['post_date', 'author']
    search_fields = ['content', 'author__username', 'blog__title']
    raw_id_fields = ['author', 'blog']
    date_hierarchy = 'post_date'
    readonly_fields = ['post_date']
    
    def truncated_content(self, obj):
        return obj.content[:75] + '...' if len(obj.content) > 75 else obj.content
    truncated_content.short_description = 'Comment'
    
    def like_count(self, obj):
        return obj.likes.count()
    like_count.short_description = 'Likes'

@admin.register(BlogAuthor)
class BlogAuthorAdmin(admin.ModelAdmin):
    list_display = ['user', 'website', 'post_count']
    search_fields = ['user__username', 'bio']
    list_filter = ('user__is_active',)
    raw_id_fields = ('user',)
    
    def post_count(self, obj):
        return obj.blog_set.count()
    post_count.short_description = 'Number of Posts'

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'post_date', 'status', 'likes_count']
    list_filter = ['status', 'post_date', 'author', 'categories']
    search_fields = ['title', 'content', 'author__user__username']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'post_date'
    filter_horizontal = ('categories', 'tags', 'likes')
    inlines = [CommentInline]
    
    fieldsets = (
        ('Post Information', {
            'fields': ('title', 'slug', 'author', 'featured_image', 'content')
        }),
        ('Categorization', {
            'fields': ('categories', 'tags')
        }),
        ('Publication', {
            'fields': ('status', 'post_date')
        }),
        ('Engagement', {
            'fields': ('views', 'likes'),
            'classes': ('collapse',)
        })
    )
    
    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes'
