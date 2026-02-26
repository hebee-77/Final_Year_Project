from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    # System Feedback
    path('submit/', views.feedback_submit, name='feedback_submit'),
    path('my-feedback/', views.my_feedback, name='my_feedback'),
    
    # Admin Feedback Management
    path('manage/', views.feedback_manage, name='feedback_manage'),
    path('<int:pk>/review/', views.feedback_review, name='feedback_review'),
    
    # Satisfaction Surveys
    path('survey/<int:course_pk>/', views.survey_create, name='survey_create'),
    path('surveys/', views.survey_list, name='survey_list'),
]
