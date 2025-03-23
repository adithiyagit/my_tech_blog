from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('blogs/', views.BlogListView.as_view(), name='blogs'),
    path('blog/<slug:slug>/', views.BlogDetailView.as_view(), name='blog-detail'),
    path('bloggers/', views.BloggerListView.as_view(), name='bloggers'),
    path('blogger/<int:pk>/', views.BloggerDetailView.as_view(), name='blogger-detail'),
    path('blog/<slug:slug>/comment/', views.add_comment, name='add-comment'),
    path('comment/<int:pk>/like/', views.like_comment, name='like-comment'),
    path('blog/<slug:slug>/like/', views.like_blog, name='like-blog'),
    path('toggle-dark-mode/', views.toggle_dark_mode, name='toggle-dark-mode'),
]