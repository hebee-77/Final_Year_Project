from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    # Assignment URLs
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('assignments/create/', views.assignment_create, name='assignment_create'),
    path('assignments/<int:pk>/edit/', views.assignment_edit, name='assignment_edit'),
    path('assignments/<int:pk>/delete/', views.assignment_delete, name='assignment_delete'),
    
    # Submission URLs
    path('assignments/<int:assignment_pk>/submit/', views.submit_assignment, name='submit_assignment'),
    path('submissions/', views.submission_list, name='submission_list'),
    path('submissions/<int:pk>/', views.submission_detail, name='submission_detail'),
    path('submissions/<int:pk>/grade/', views.grade_submission, name='grade_submission'),
    
    # AI Feedback URLs
    path('submissions/<int:pk>/ai-feedback/generate/', views.generate_ai_feedback, name='generate_ai_feedback'),
    path('submissions/<int:pk>/ai-feedback/', views.ai_feedback_view, name='ai_feedback'),
]
