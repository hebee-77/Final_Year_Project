from django import forms
from .models import Course, LearningMaterial, LearningGoal, Subject

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'subject', 'description', 'thumbnail', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class LearningMaterialForm(forms.ModelForm):
    class Meta:
        model = LearningMaterial
        fields = ['title', 'material_type', 'content', 'file', 'external_link', 'order']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 8}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class LearningGoalForm(forms.ModelForm):
    class Meta:
        model = LearningGoal
        fields = ['course', 'goal_text', 'target_date']
        widgets = {
            'target_date': forms.DateInput(attrs={'type': 'date'}),
            'goal_text': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.is_student():
            self.fields['course'].queryset = user.enrolled_courses.all()
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
