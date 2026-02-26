from django.contrib import admin
from .models import Subject, Course, LearningMaterial, LearningGoal

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'created_by', 'created_at']
    search_fields = ['name', 'code']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'teacher', 'is_active', 'created_at']
    list_filter = ['is_active', 'subject', 'created_at']
    search_fields = ['title', 'description']
    filter_horizontal = ['enrolled_students']

@admin.register(LearningMaterial)
class LearningMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'material_type', 'order', 'created_at']
    list_filter = ['material_type', 'course']
    search_fields = ['title', 'course__title']

@admin.register(LearningGoal)
class LearningGoalAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'is_completed', 'target_date']
    list_filter = ['is_completed', 'course']
    search_fields = ['student__username', 'goal_text']
