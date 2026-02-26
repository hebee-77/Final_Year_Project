from django.db import models
from accounts.models import User

class Subject(models.Model):
    """Subject/Course categories"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Course(models.Model):
    """Learning courses"""
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='courses')
    description = models.TextField()
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='courses_teaching')
    enrolled_students = models.ManyToManyField(User, related_name='enrolled_courses', blank=True)
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class LearningMaterial(models.Model):
    """Course learning materials"""
    
    class MaterialType(models.TextChoices):
        PDF = 'PDF', 'PDF Document'
        VIDEO = 'VIDEO', 'Video'
        TEXT = 'TEXT', 'Text Content'
        LINK = 'LINK', 'External Link'
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    material_type = models.CharField(max_length=10, choices=MaterialType.choices)
    content = models.TextField(blank=True, null=True)  # For text content
    file = models.FileField(upload_to='learning_materials/', blank=True, null=True)
    external_link = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class LearningGoal(models.Model):
    """Student learning goals"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_goals')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='student_goals')
    goal_text = models.TextField()
    target_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    completed_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.goal_text[:50]}"
