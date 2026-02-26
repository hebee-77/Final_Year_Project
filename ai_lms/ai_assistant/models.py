from django.db import models
from accounts.models import User
from content.models import Course

class AIConversation(models.Model):
    """Store AI chat conversations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_conversations')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class AIMessage(models.Model):
    """Individual messages in AI conversations"""
    
    class MessageType(models.TextChoices):
        USER = 'USER', 'User Message'
        AI = 'AI', 'AI Response'
    
    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MessageType.choices)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.message_type} - {self.created_at}"


class AIGeneratedContent(models.Model):
    """AI-generated learning content"""
    
    class ContentType(models.TextChoices):
        SUMMARY = 'SUMMARY', 'Summary'
        EXPLANATION = 'EXPLANATION', 'Explanation'
        PRACTICE = 'PRACTICE', 'Practice Questions'
        CONCEPT_MAP = 'CONCEPT_MAP', 'Concept Map'
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    content_type = models.CharField(max_length=20, choices=ContentType.choices)
    prompt = models.TextField()
    generated_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.content_type}"
