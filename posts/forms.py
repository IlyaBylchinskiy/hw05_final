from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post
from taggit.forms import TagField

User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image', 'tags')
        labels = {
            'group': 'Группа',
            'text': 'Текст заметки',
            'image': 'Картинка заметки',
            'tags': 'Тэги'
        }
        widgets = {
            'text': forms.Textarea(attrs={'style':
                                          'resize: vertical;'})
        }

    # tags = TagField(label='Тэги')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )
        labels = {'text': 'Текст комментариями'}
        widgets = {
            'text': forms.Textarea(attrs={'style':
                                          'resize: vertical;'})
        }
