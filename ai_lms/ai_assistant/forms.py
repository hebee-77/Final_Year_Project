from django import forms
from content.models import Course

class AIPromptForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'Enter the content you want to summarize...'
        }),
        label='Content'
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Related Course (optional)'
    )
