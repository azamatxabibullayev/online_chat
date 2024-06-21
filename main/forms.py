from django import forms
from django.contrib.auth.models import User
from .models import Message, Chat


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text', 'file', 'receiver']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }


class GroupForm(forms.ModelForm):
    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    participants = forms.ModelMultipleChoiceField(queryset=User.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Chat
        fields = ['title', 'description', 'participants']
