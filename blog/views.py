from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment, Category, FollowedCategory
from django.db.models import Count
from django.contrib.auth.models import User
from django.views.generic import (ListView,
 								DetailView,
  								CreateView,
  								UpdateView,
  								DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from blog.forms import AddCommentForm, AddPostForm, AddCategoryForm
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib import messages
# from django.http import HttpResponse

def home(request):
	context = {
		'posts': Post.objects.all()
	}
	return render(request, 'blog/home.html', context) #views need to return HttpResponse or Exception

def get_top3List(posts):
	postVoteList = []
	for post in posts:
		postVoteList.append((post.id, post.get_upVotes()-post.get_downVotes()))
	postVoteList.sort(key = lambda x: x[1], reverse=True)
	length = len(postVoteList)	
	if length>2:
		postVoteList = postVoteList[:3]
		length = 3
	finalTop3List = []
	for post in postVoteList:
		finalTop3List.append(Post.objects.annotate(comment_count=Count('comments')).get(id=post[0]))
	return finalTop3List, length

class PostListView(ListView):
	model = Post
	template_name = 'blog/home.html'
	context_object_name = 'posts'
	# ordering = ['-date_posted']
	paginate_by= 5

	def get_queryset(self):
		return Post.objects.annotate(comment_count=Count('comments')).order_by('-date_posted')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		finalTop3List, length = get_top3List(Post.objects.all())
		context['length'] = length
		context['top3posts'] = finalTop3List
		return context

def get_categoriesList(username):
	user = get_object_or_404(User, username=username)
	categories = FollowedCategory.objects.filter(user=user)
	categoriesList = []
	for category in categories:
		categoriesList.append(category.category)
	return categoriesList

class FollowedPostListView(ListView):
	model = Post
	template_name = 'blog/home.html'
	context_object_name = 'posts'
	paginate_by= 5

	def get_queryset(self):
		categoriesList = get_categoriesList(self.kwargs.get('username'))
		return Post.objects.filter(category__in=categoriesList).annotate(comment_count=Count('comments')).order_by('-date_posted')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		categoriesList = get_categoriesList(self.kwargs.get('username'))
		finalTop3List, length = get_top3List(Post.objects.filter(category__in=categoriesList))
		context['length'] = length
		context['top3posts'] = finalTop3List
		context['top3Header'] = f'in followed categories'
		return context

class UserPostListView(ListView):
	model = Post
	template_name = 'blog/user_posts.html'
	context_object_name = 'posts'
	paginate_by = 5

	def get_queryset(self):
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		return Post.objects.annotate(comment_count=Count('comments')).filter(author=user).order_by('-date_posted')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		finalTop3List, length = get_top3List(Post.objects.filter(author=user))
		context['length'] = length
		context['top3posts'] = finalTop3List
		context['top3Header'] = f'by {user}'
		return context

	# def get_context_data(self, **kwargs):
	# 	post = self.get_object()
	# 	upVoted = 0
	# 	context = super().get_context_data(**kwargs)
	# 	context['totalVotes'] = post.get_upVotes() - post.get_downVotes()
	# 	if post.upVotes.filter(id=self.request.user.id).exists():
	# 		upVoted = 1
	# 	elif post.downVotes.filter(id=self.request.user.id).exists():
	# 		upVoted = -1
	# 	context['upVoted'] = upVoted
	# 	return context

	# def get_context_data(self, **kwargs):
	# 	context = super().get_context_data(**kwargs)
	# 	print(context)
	# 	user = get_object_or_404(User, username=self.kwargs.get('username'))
	# 	posts = Post.objects.filter(author=user).order_by('-date_posted')
	# 	page_obj = Paginator(posts, 5)
	# 	context['posts'] = page_obj.page(1)
	# 	context['page_obj'] = page_obj
	# 	return context

class PostDetailView(DetailView):
	model = Post
	form = AddCommentForm
	# upVoteForm = UpVoteForm

	def post(self, request, *args, **kwargs):
		form = AddCommentForm(request.POST)
		upVoteForm = AddCommentForm(request.POST)

		if form.is_valid():
			post = self.get_object()
			form.instance.author = request.user
			form.instance.parent_post = post
			form.save()
			return redirect(reverse('post-detail', kwargs={'pk': self.kwargs['pk']}))
	def get_context_data(self, **kwargs):
		post = self.get_object()
		upVoted = 0
		context = super().get_context_data(**kwargs)
		context['form'] = self.form
		# context['upVotes'] = post.get_upVotes()
		# context['downVotes'] = post.get_downVotes()
		context['totalVotes'] = post.get_upVotes() - post.get_downVotes()
		if post.upVotes.filter(id=self.request.user.id).exists():
			upVoted = 1
		elif post.downVotes.filter(id=self.request.user.id).exists():
			upVoted = -1
		context['upVoted'] = upVoted
		context['comments'] = Comment.objects.all().filter(parent_post=self.kwargs['pk']).order_by('-date_posted')

		return context

class PostCreateView(LoginRequiredMixin, CreateView):
	model = Post
	fields = ['title', 'content', 'category']

	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)

# @login_required
# def PostCreate(request):
# 	template_name = 'blog/post_form.html'
# 	if request.method == 'POST':
# 		print(request.POST)
# 		form = AddPostForm(request.POST)
# 		if form.is_valid():
# 			form.instance.author = request.user
# 			form.save()
# 			# return redirect('post-create')
# 			# return reverse('post-detail', kwargs={'pk': self.pk})
# 	else:
# 		form = AddPostForm()
# 		return render (request, template_name, {'form': form})

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

# class CommentCreateView(LoginRequiredMixin, FormView):
# 	model = Comment
# 	template_name = 'blog/post_detail.html'
# 	fields = ['content']

# 	def form_valid(self, form):
# 		form.instance.author = self.request.user
# 		return super().form_valid(form)


def about(request):
	context = {
		'title': 'About'
	}
	return render(request, 'blog/about.html', context)
	# return HttpResponse("<h1>Blog About</h1>")

def UpVoting(request, pk):
	upvote_type = 'post_id_upvote'
	model_name = Post
	# if 'user_post_id_upvote' in request.POST:
	# 	upvote_type = 'user_post_id_upvote'
	if 'comment_id_upvote' in request.POST:
		upvote_type = 'comment_id_upvote'
		model_name = Comment
	post = get_object_or_404(model_name, id=request.POST.get(upvote_type))
	upVoted = False
	if post.upVotes.filter(id=request.user.id).exists():
		post.upVotes.remove(request.user)
		upVoted = False
	else:
		post.upVotes.add(request.user)
		upVoted = True
	if upVoted:
		if post.downVotes.filter(id=request.user.id).exists():
			post.downVotes.remove(request.user)
	# if 'user_post_id_upvote' in request.POST:
	# 	return redirect(reverse('user-posts', kwargs={'username': post.author}))
	return redirect(reverse('post-detail', kwargs={'pk': pk}))

def DownVoting(request, pk):
	downvote_type = 'post_id_downvote'
	model_name = Post
	if 'comment_id_downvote' in request.POST:
		downvote_type = 'comment_id_downvote'
		model_name = Comment
	post = get_object_or_404(model_name, id=request.POST.get(downvote_type))
	downVoted = False
	if post.downVotes.filter(id=request.user.id).exists():
		post.downVotes.remove(request.user)
		downVoted = False
	else:
		post.downVotes.add(request.user)
		downVoted = True
	if downVoted:
		if post.upVotes.filter(id=request.user.id).exists():
			post.upVotes.remove(request.user)
	return redirect(reverse('post-detail', kwargs={'pk': pk}))

	# if 'upVote' in request.POST:
	# 	print("22222222222")
	# 	post = self.get_object()
	# 	upVoteForm.instance.voter = request.user
	# 	upVoteForm.instance.parent_post = post
	# 	voteCount = Post.objects.get(pk=self.kwargs['pk']).get_upVotes_and_downVotes()
	# 	upVoteForm.instance.upVote = voteCount['upVotes']+1
	# 	upVoteForm.instance.downVote = voteCount['downVotes']
	# 	print(vars(upVoteForm))
	# 	# print(obj)
	# 	upVoteForm.save()
		# return redirect(reverse('post-detail', kwargs={'pk': self.kwargs['pk']}))

class UserCommentListView(ListView):
	model = Comment
	template_name = 'blog/user_posts.html'
	context_object_name = 'comments'
	paginate_by = 7

	def get_queryset(self):
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		return Comment.objects.filter(author=user).order_by('-date_posted')

class CategoryPostListView(ListView):
	model = Post
	template_name = 'blog/category_posts.html'
	context_object_name = 'posts'
	paginate_by = 5

	def get_queryset(self):
		category = get_object_or_404(Category, name=self.kwargs.get('category').replace('-',' '))
		return Post.objects.annotate(comment_count=Count('comments')).filter(category=category).order_by('-date_posted')

	def get_context_data(self, **kwargs):
		category = get_object_or_404(Category, name=self.kwargs.get('category').replace('-',' '))
		context = super().get_context_data(**kwargs)
		finalTop3List, length = get_top3List(Post.objects.filter(category=category))
		context['length'] = length
		context['top3posts'] = finalTop3List
		context['top3Header'] = f'in {category}'
		return context

class CategoryCreateView(LoginRequiredMixin, CreateView):
	model = Category
	form_class = AddCategoryForm
	template_name = 'blog/category_form.html'
	def post(self, request, *args, **kwargs):
		form = AddCategoryForm(request.POST)
		if form.is_valid():
			try:
				form.save()
				return redirect(reverse('post-create'))
			except IntegrityError:
				messages.error(request, 'Category with that name ALREADY EXISTS!')
				return redirect(reverse('category-create'))

@login_required
def followCategory(request):
	user = request.user

	if 'category_follow' in request.POST:
		catName = request.POST.get('category_follow')
		category = get_object_or_404(Category, name=catName)
		ifExists = FollowedCategory.objects.filter(user=user, category=category)
		if not ifExists:
			addNewFollow = FollowedCategory(user=user, category=category)
			addNewFollow.save()

	elif 'category_unfollow' in request.POST:
		catName = request.POST.get('category_unfollow')
		category = get_object_or_404(Category, name=catName)
		ifExists = FollowedCategory.objects.filter(user=user, category=category)
		if ifExists:
			removeFollow = ifExists.delete()

	return redirect(reverse('category-posts', kwargs={'category': catName}))



def handle404error(request, exception):
	return render(request, '404error.html')