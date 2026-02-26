from django.contrib import admin
from .models import Assignment, Submission, AIFeedback, TeacherFeedback


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'status', 'due_date', 'max_score', 'created_by', 'created_at']
    list_filter = ['status', 'course', 'created_at']
    search_fields = ['title', 'description', 'course__title']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'title', 'status')
        }),
        ('Content', {
            'fields': ('description', 'instructions', 'attachment')
        }),
        ('Grading & Due Date', {
            'fields': ('max_score', 'due_date')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'status', 'score', 'submitted_at', 'is_late']
    list_filter = ['status', 'submitted_at', 'assignment__course']
    search_fields = ['student__username', 'student__email', 'assignment__title']
    readonly_fields = ['submitted_at', 'graded_at']
    
    def is_late(self, obj):
        return obj.is_late
    is_late.boolean = True
    is_late.short_description = 'Late Submission'


@admin.register(AIFeedback)
class AIFeedbackAdmin(admin.ModelAdmin):
    list_display = ['submission', 'generated_at']
    readonly_fields = ['generated_at']
    search_fields = ['submission__student__username']


@admin.register(TeacherFeedback)
class TeacherFeedbackAdmin(admin.ModelAdmin):
    list_display = ['submission', 'teacher', 'created_at']
    list_filter = ['created_at', 'teacher']
    search_fields = ['submission__student__username', 'teacher__username', 'feedback_text']
    readonly_fields = ['created_at', 'updated_at']
