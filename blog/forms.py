from django import forms
from .models import Comment, Post, Category

categoryChoices = Category.objects.all().values_list('name','name')
choiceList = []
for item in categoryChoices:
	choiceList.append(item)

class AddCommentForm(forms.ModelForm):
	content = forms.CharField(widget = forms.Textarea(attrs = {
		'rows': '4',
		'class': 'md-textarea form-control',
		'placeholder': 'Comment here..'
		}))
	class Meta:
		model = Comment
		fields = ['content']

class AddPostForm(forms.ModelForm):
	class Meta:
		model = Post
		fields = ['title', 'content', 'category']

class AddCategoryForm(forms.ModelForm):
	class Meta:
		model = Category
		fields = ['name']

	def clean(self):
		for field, value in self.cleaned_data.items():
			self.cleaned_data['name'] = value.lower()