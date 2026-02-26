from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    # Chat Interface
    path('chat/', views.chat_interface, name='chat'),
    path('chat/<int:conversation_id>/', views.chat_interface, name='chat_conversation'),
    path('chat/send/', views.send_message, name='send_message'),
    path('chat/conversations/', views.conversation_list, name='conversation_list'),
    path('chat/conversations/<int:pk>/delete/', views.conversation_delete, name='conversation_delete'),
    
    # AI Content Generation
    path('generate/summary/', views.generate_summary, name='generate_summary'),
    path('generate/explanation/', views.generate_explanation, name='generate_explanation'),
    path('generate/questions/', views.generate_questions, name='generate_questions'),
    
    # AI History
    path('history/', views.ai_history, name='ai_history'),
]
