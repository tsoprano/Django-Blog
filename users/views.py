from django.shortcuts import render, redirect
# from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, PasswordUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from blog.models import FollowedCategory

def register(request):
	if request.method == 'POST':
		form = UserRegisterForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			messages.success(request, f'Account created for {username}! You can now login.')
			return redirect('login')
	else:
		form = UserRegisterForm()
	return render (request, 'users/register.html', {'form': form})

@login_required
def profile(request):
	if request.method == 'POST':
		u_form = UserUpdateForm(request.POST, instance=request.user)
		p_form = ProfileUpdateForm(request.POST,
								   request.FILES,
								   instance=request.user.profile)
		pass_form = PasswordUpdateForm(user=request.user, data = request.POST)
		if u_form.is_valid() and p_form.is_valid() and pass_form.is_valid():
			u_form.save()
			p_form.save()
			pass_form.save()
			messages.success(request, f'Account updated for {request.user.username}! You can now login.')
			return redirect('profile')
	else:
		print(request.user)
		u_form = UserUpdateForm(instance=request.user)
		p_form = ProfileUpdateForm(instance=request.user.profile)
		pass_form = PasswordUpdateForm(user=request.user)

	user_categories = []
	followed = FollowedCategory.objects.filter(user=request.user)
	for tup in followed:
		user_categories.append(tup.category)

	context = {
		'u_form': u_form,
		'p_form': p_form,
		'pass_form': pass_form,
		'user_categories': user_categories
	}
	return render (request, 'users/profile.html', context)

# class ChangePasswordView(PasswordChangeView, LoginRequiredMixin, UserPassesTestMixin):
# 	form_class = Password 