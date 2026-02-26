from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Student Analytics
    path('progress/', views.student_progress, name='student_progress'),
    path('progress/<int:course_pk>/', views.course_progress_detail, name='course_progress_detail'),
    path('activities/', views.activity_log, name='activity_log'),
    
    # Teacher Analytics
    path('class-analytics/<int:course_pk>/', views.class_analytics, name='class_analytics'),
    path('student-performance/<int:student_pk>/', views.student_performance, name='student_performance'),
    
    # Admin Analytics
    path('system-analytics/', views.system_analytics, name='system_analytics'),
    path('engagement-metrics/', views.engagement_metrics, name='engagement_metrics'),
]
