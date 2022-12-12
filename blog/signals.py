from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import Category, FollowedCategory
from django.dispatch import receiver

# @receiver(post_save, sender=Category)
# def add_follower(sender, instance, created, **kwargs):
# 	if created:
# 		print("--------------------------------------------------------------")
# 		print(instance)
# 		FollowedCategory.objects.create(user=user, category=instance)

