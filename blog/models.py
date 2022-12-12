from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Sum
from ckeditor.fields import RichTextField
# from django.utils import timezone

class Category(models.Model):
	name = models.CharField(max_length = 100, unique=True)

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('post-create')

	def get_followers(self):
		followerList = FollowedCategory.objects.filter(category = self.id)
		followers = []
		for follower in followerList:
			followers.append(follower.user.username)
		return followers


class Post(models.Model):
	title = models.CharField(max_length = 100)
	# content = models.TextField()
	content = RichTextField(blank=True, null=True)
	date_posted = models.DateTimeField(auto_now_add=True)
	# date_posted = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	upVotes = models.ManyToManyField(User, related_name='blog_upvotes', blank=True)
	downVotes = models.ManyToManyField(User, related_name='blog_downvotes', blank=True)
	category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='blog_category', default=1)

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('post-detail', kwargs={'pk': self.pk})

	def get_upVotes(self):
		return self.upVotes.count()

	def get_downVotes(self):
		return self.downVotes.count()

	# def get_upVotes_and_downVotes(self):
	# 	voteObj = Vote.objects.filter(parent_post_id=self.pk)
	# 	uV = voteObj.aggregate(Sum('upVote'))['upVote__sum']
	# 	dV = voteObj.aggregate(Sum('downVote'))['downVote__sum']
	# 	return {'upVotes':uV, 'downVotes':dV, 'totalVotes': uV+dV}

class Comment(models.Model):
	content = models.TextField()
	date_posted = models.DateTimeField(auto_now_add=True)
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'comment_author')
	parent_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name = 'comments')
	upVotes = models.ManyToManyField(User, related_name='comment_upvotes', blank=True)
	downVotes = models.ManyToManyField(User, related_name='comment_downvotes', blank=True)

	def __str__(self):
		return self.content[:10]

	def get_upVotes(self):
		return self.upVotes.count()

	def get_downVotes(self):
		return self.downVotes.count()

	def get_totalVotes(self):
		return self.upVotes.count() - self.downVotes.count()

# class Vote(models.Model):
# 	upVote = models.IntegerField(default=1)
# 	downVote = models.IntegerField(default=1)
# 	voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'voter')
# 	parent_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name = 'votes')

# 	def __str__(self):
# 		return self.voter.username

class FollowedCategory(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='user_category', blank=True, null=True)

	def __str__(self):
		return f'{self.user.username} -> {self.category.name}'

	# def get_categories(self):