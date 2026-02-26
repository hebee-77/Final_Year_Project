from django.db import models
from accounts.models import User
from content.models import Course

class StudentProgress(models.Model):
    """Track student progress in courses"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_records')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='student_progress')
    materials_completed = models.PositiveIntegerField(default=0)
    total_materials = models.PositiveIntegerField(default=0)
    completion_percentage = models.FloatField(default=0.0)
    time_spent_minutes = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title}"


class LearningActivity(models.Model):
    """Log student learning activities"""
    
    class ActivityType(models.TextChoices):
        MATERIAL_VIEW = 'MATERIAL_VIEW', 'Viewed Material'
        ASSIGNMENT_SUBMIT = 'ASSIGNMENT_SUBMIT', 'Submitted Assignment'
        AI_INTERACTION = 'AI_INTERACTION', 'AI Interaction'
        GOAL_SET = 'GOAL_SET', 'Set Goal'
        GOAL_COMPLETE = 'GOAL_COMPLETE', 'Completed Goal'
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    activity_type = models.CharField(max_length=20, choices=ActivityType.choices)
    description = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Learning Activities'
    
    def __str__(self):
        return f"{self.student.username} - {self.activity_type}"


class EngagementMetrics(models.Model):
    """Aggregate engagement metrics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='engagement_metrics')
    date = models.DateField()
    total_time_minutes = models.PositiveIntegerField(default=0)
    materials_viewed = models.PositiveIntegerField(default=0)
    ai_interactions = models.PositiveIntegerField(default=0)
    assignments_submitted = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"
