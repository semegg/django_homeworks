from django import forms

from .models import Comment, Post


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)

        widgets = {
            'body': forms.Textarea(attrs={'placeholder': 'Share your thoughts in the comments...',
                                          'class': 'form-control',
                                          'rows': 4})
        }

        labels = {
            'body': 'Add your comment'
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'body', 'status', 'image_url', 'category')

        labels = {
            'category': 'Post category',
            'title': 'Post title',
            'body': 'Post content',
            'image_url': 'Url to post image'
        }

        widgets = {
            'category': forms.Select(attrs={'class': 'form-control border border-4 rounded-pill'}),
            'title': forms.TextInput(attrs={'class': 'form-control border border-4 rounded-pill',
                                            'placeholder': 'Enter a title'}),
            'body': forms.Textarea(attrs={'class': 'form-control border border-4',
                                          'placeholder': 'Enter a content'}),
            'status': forms.Select(attrs={'class': 'form-control border border-4 rounded-pill'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control border border-4 rounded-pill',
                                        'placeholder': 'Enter a image URL'})
        }


