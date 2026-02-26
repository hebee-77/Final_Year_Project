from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Custom User model with role-based access"""
    
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        TEACHER = 'TEACHER', _('Teacher')
        STUDENT = 'STUDENT', _('Student')
    
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    def is_teacher(self):
        return self.role == self.Role.TEACHER
    
    def is_student(self):
        return self.role == self.Role.STUDENT


class StudentProfile(models.Model):
    """Extended profile for students"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    enrollment_date = models.DateField(auto_now_add=True)
    grade_level = models.CharField(max_length=50, blank=True)
    learning_preferences = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"Student: {self.user.username}"


class TeacherProfile(models.Model):
    """Extended profile for teachers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    specialization = models.CharField(max_length=200)
    qualification = models.TextField()
    join_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"Teacher: {self.user.username}"
