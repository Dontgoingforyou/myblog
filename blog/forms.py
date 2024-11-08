from django import forms

from blog.models import Comment


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25, label='Имя')
    email = forms.EmailField(label='Ваш Email')
    to = forms.EmailField(label='Email получателя')
    comments = forms.CharField(required=False, widget=forms.Textarea, label='Комментарий')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']