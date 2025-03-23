from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import BlogAuthor, Blog, Comment

class BlogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user(username='testuser', password='12345')
        test_author = BlogAuthor.objects.create(user=test_user, bio='This is a test.')
        Blog.objects.create(title='Test Blog', content='Test Content', author=test_author)

    def test_blog_list_view(self):
        response = self.client.get(reverse('blogs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog_list.html')

    def test_blog_pagination(self):
        user = User.objects.get(username='testuser')
        author = BlogAuthor.objects.get(user=user)
        
        # Create 6 blogs for pagination tests
        for i in range(6):
            Blog.objects.create(title=f'Test Blog {i}', content='Test Content', author=author)
            
        response = self.client.get(reverse('blogs'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['blog_list']), 5)

# Create your tests here.
