from django.db import models
from accounts.models import User
from content.models import Course

class SystemFeedback(models.Model):
    """User feedback on the system"""
    
    class FeedbackType(models.TextChoices):
        BUG = 'BUG', 'Bug Report'
        FEATURE = 'FEATURE', 'Feature Request'
        GENERAL = 'GENERAL', 'General Feedback'
        AI_QUALITY = 'AI_QUALITY', 'AI Quality'
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        REVIEWED = 'REVIEWED', 'Reviewed'
        RESOLVED = 'RESOLVED', 'Resolved'
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback_submitted')
    feedback_type = models.CharField(max_length=20, choices=FeedbackType.choices)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedback_reviewed')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'System Feedback'
    
    def __str__(self):
        return f"{self.user.username} - {self.subject}"


class SatisfactionSurvey(models.Model):
    """Course satisfaction surveys"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='satisfaction_surveys')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='surveys_completed')
    content_quality_rating = models.PositiveSmallIntegerField()  # 1-5
    ai_assistance_rating = models.PositiveSmallIntegerField()  # 1-5
    overall_satisfaction = models.PositiveSmallIntegerField()  # 1-5
    comments = models.TextField(blank=True)
    would_recommend = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['course', 'student']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title} Survey"
