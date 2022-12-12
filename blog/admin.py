from django.contrib import admin
from .models import Post, Comment, Category, FollowedCategory

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(FollowedCategory)
# admin.site.register(Vote)
