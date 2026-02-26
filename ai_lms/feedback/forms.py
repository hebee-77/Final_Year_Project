from django import forms
from .models import SystemFeedback, SatisfactionSurvey

class SystemFeedbackForm(forms.ModelForm):
    class Meta:
        model = SystemFeedback
        fields = ['feedback_type', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 6}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class SatisfactionSurveyForm(forms.ModelForm):
    class Meta:
        model = SatisfactionSurvey
        fields = [
            'content_quality_rating',
            'ai_assistance_rating',
            'overall_satisfaction',
            'would_recommend',
            'comments'
        ]
        widgets = {
            'content_quality_rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'ai_assistance_rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'overall_satisfaction': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'comments': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'content_quality_rating': 'Content Quality (1-5)',
            'ai_assistance_rating': 'AI Assistance (1-5)',
            'overall_satisfaction': 'Overall Satisfaction (1-5)',
            'would_recommend': 'Would you recommend this course?',
            'comments': 'Additional Comments (optional)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'would_recommend':
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            else:
                self.fields[field].widget.attrs.update({'class': 'form-check-input'})
