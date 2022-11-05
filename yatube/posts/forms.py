from django import forms

from .models import Comment, Group, Post

COUNT_CHAR_TEXT = 10


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def clean_text(self):
        data = self.cleaned_data['text']
        if len(data) < COUNT_CHAR_TEXT:
            raise forms.ValidationError('Поле должно быть больше 10')
        return data


class GroupForm(forms.ModelForm):

    description = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Group
        fields = ('title', 'slug', 'description')

    def clean_slug(self):
        data = self.cleaned_data['slug']
        if len(data) > COUNT_CHAR_TEXT:
            raise forms.ValidationError('Поле должно быть меньше 10')
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
