from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    # Course URLs
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    path('courses/<int:pk>/enroll/', views.course_enroll, name='course_enroll'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:pk>/edit/', views.course_edit, name='course_edit'),
    
    # Learning Material URLs
    path('materials/<int:pk>/', views.material_detail, name='material_detail'),
    path('courses/<int:course_pk>/materials/create/', views.material_create, name='material_create'),
    path('materials/<int:pk>/edit/', views.material_edit, name='material_edit'),
    path('materials/<int:pk>/delete/', views.material_delete, name='material_delete'),
    
    # Learning Goals URLs
    path('goals/', views.goal_list, name='goal_list'),
    path('goals/create/', views.goal_create, name='goal_create'),
    path('goals/<int:pk>/complete/', views.goal_complete, name='goal_complete'),
    
    # Subject URLs
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),
]
