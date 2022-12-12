from django.urls import path
from . import views
from .views import (PostListView,
                    FollowedPostListView,
                    PostDetailView,
                    PostCreateView,
                    PostUpdateView,
                    PostDeleteView,
                    UserPostListView,
                    UpVoting,
                    DownVoting,
                    UserCommentListView,
                    # PostCreate,
                    CategoryPostListView,
                    CategoryCreateView,
                    followCategory,)

urlpatterns = [
    # path('', views.home, name='blog-home'),
    path('', PostListView.as_view(), name='blog-home'),
    path('followed/<str:username>', FollowedPostListView.as_view(), name='blog-home-followed'),
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'),
    path('post/<int:pk>', PostDetailView.as_view(), name='post-detail'),
    path('post/new', PostCreateView.as_view(), name='post-create'),
    # path('post/new', PostCreate, name='post-create'),
    path('post/<int:pk>/update', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete', PostDeleteView.as_view(), name='post-delete'),
    path('about/', views.about, name='blog-about'),
    path('upVote/<int:pk>', UpVoting, name='upvote_post'),
    path('downVote/<int:pk>', DownVoting, name='downvote_post'),
    path('user/comments/<str:username>', UserCommentListView.as_view(), name='user-comments'),
    path('category/<str:category>', CategoryPostListView.as_view(), name='category-posts'),
    path('category/create/new', CategoryCreateView.as_view(), name='category-create'),
    path('follow/', followCategory, name='follow_category'),

]