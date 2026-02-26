from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Assignment, Submission, TeacherFeedback
from content.models import Course


class AssignmentForm(forms.ModelForm):
    """Form for creating and editing assignments"""
    
    class Meta:
        model = Assignment
        fields = ['course', 'title', 'description', 'instructions', 'max_score', 'due_date', 'status', 'attachment']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Assignment Title'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 8,
                'placeholder': 'Enter assignment questions here:\n\n1. What are the main causes of...?\n2. Explain the concept of...\n3. Analyze the following...'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 5,
                'placeholder': 'Instructions:\n- Review all materials\n- Cite your sources\n- Minimum 500 words\n- Submit before due date'
            }),
            'max_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'value': 100}),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'type': 'datetime-local'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'description': 'Assignment Questions *',
            'instructions': 'Instructions for Students',
            'attachment': 'Attachment (Optional)',
        }
    
    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter courses for teachers
        if teacher and teacher.is_teacher:
            self.fields['course'].queryset = teacher.courses_teaching.all()
        
        # Set default due date
        if not self.instance.pk:
            default_due = timezone.now() + timedelta(days=7)
            self.initial['due_date'] = default_due.strftime('%Y-%m-%dT%H:%M')


class SubmissionForm(forms.ModelForm):
    """Form for student submissions"""
    
    class Meta:
        model = Submission
        fields = ['content', 'file']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 12,
                'placeholder': 'Write your complete answer here...\n\nMake sure to:\n- Answer all parts of the question\n- Show your work\n- Provide examples where applicable'
            }),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'content': 'Your Answer *',
            'file': 'Attach File (Optional)',
        }


class GradeForm(forms.ModelForm):
    """Form for grading submissions"""
    
    class Meta:
        model = Submission
        fields = ['score']
        widgets = {
            'score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01',
                'placeholder': 'Enter score'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.assignment:
            max_score = self.instance.assignment.max_score
            self.fields['score'].widget.attrs['max'] = max_score
            self.fields['score'].help_text = f'Out of {max_score} points'


class TeacherFeedbackForm(forms.ModelForm):
    """Form for teacher feedback"""
    
    class Meta:
        model = TeacherFeedback
        fields = ['feedback_text']
        widgets = {
            'feedback_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Provide constructive feedback:\n\nStrengths:\n- Good analysis of...\n\nAreas for improvement:\n- Consider adding...\n\nSuggestions:\n- Review the concept of...'
            }),
        }
        labels = {
            'feedback_text': 'Your Feedback *',
        }
