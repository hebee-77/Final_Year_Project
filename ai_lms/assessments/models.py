from django.db import models
from django.utils import timezone
from accounts.models import User
from content.models import Course


class Assignment(models.Model):
    """Course assignments"""
    
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PUBLISHED = 'PUBLISHED', 'Published'
        CLOSED = 'CLOSED', 'Closed'
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Assignment questions or description")
    instructions = models.TextField(help_text="Detailed instructions for students")
    max_score = models.PositiveIntegerField(default=100)
    due_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    attachment = models.FileField(upload_to='assignments/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_assignments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    @property
    def is_overdue(self):
        """Check if assignment is past due date"""
        return timezone.now() > self.due_date
    
    @property
    def submission_count(self):
        """Get total number of submissions"""
        return self.submissions.count()
    
    @property
    def graded_count(self):
        """Get number of graded submissions"""
        return self.submissions.exclude(score__isnull=True).count()


class Submission(models.Model):
    """Student assignment submissions"""
    
    class Status(models.TextChoices):
        SUBMITTED = 'SUBMITTED', 'Submitted'
        GRADED = 'GRADED', 'Graded'
        RETURNED = 'RETURNED', 'Returned'
    
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    content = models.TextField(help_text="Student's answer/response")
    file = models.FileField(upload_to='submissions/', blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SUBMITTED)
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ['assignment', 'student']
        ordering = ['-submitted_at']
        verbose_name = 'Submission'
        verbose_name_plural = 'Submissions'
    
    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"
    
    @property
    def is_graded(self):
        """Check if submission has been graded"""
        return self.score is not None
    
    @property
    def is_late(self):
        """Check if submission was submitted after due date"""
        return self.submitted_at > self.assignment.due_date
    
    @property
    def percentage_score(self):
        """Calculate percentage score"""
        if self.score is not None and self.assignment.max_score > 0:
            return (self.score / self.assignment.max_score) * 100
        return None


class AIFeedback(models.Model):
    """AI-generated feedback on submissions"""
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='ai_feedback')
    feedback_text = models.TextField(blank=True)
    strengths = models.TextField(blank=True)
    improvements = models.TextField(blank=True)
    suggestions = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'AI Feedback'
        verbose_name_plural = 'AI Feedback'
    
    def __str__(self):
        return f"AI Feedback for {self.submission.student.username}"


class TeacherFeedback(models.Model):
    """Teacher feedback on submissions"""
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='teacher_feedback_set')
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='given_feedback')
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Teacher Feedback'
        verbose_name_plural = 'Teacher Feedback'
    
    def __str__(self):
        return f"Feedback by {self.teacher.username if self.teacher else 'Unknown'} for {self.submission.student.username}"


# Alias for backward compatibility
class Feedback(TeacherFeedback):
    """Alias for TeacherFeedback for backward compatibility"""
    class Meta:
        proxy = True
