from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import AIConversation, AIMessage, AIGeneratedContent
from .services import GeminiAIService
from .forms import AIPromptForm
import json

@login_required
def chat_interface(request, conversation_id=None):
    """AI chat interface"""
    if not request.user.is_student():
        messages.error(request, 'Only students can access AI assistant.')
        return redirect('core:dashboard')
    
    # Get or create conversation
    if conversation_id:
        conversation = get_object_or_404(AIConversation, pk=conversation_id, user=request.user)
        messages_list = conversation.messages.all()
    else:
        conversation = None
        messages_list = []
    
    # Get user's recent conversations
    recent_conversations = AIConversation.objects.filter(user=request.user)[:10]
    
    context = {
        'conversation': conversation,
        'messages': messages_list,
        'recent_conversations': recent_conversations,
    }
    return render(request, 'ai_assistant/chat_interface.html', context)

@login_required
@require_POST
def send_message(request):
    """Send message to AI and get response"""
    if not request.user.is_student():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        
        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Get or create conversation
        if conversation_id:
            conversation = get_object_or_404(AIConversation, pk=conversation_id, user=request.user)
        else:
            conversation = AIConversation.objects.create(
                user=request.user,
                title=user_message[:50] + ('...' if len(user_message) > 50 else '')
            )
        
        # Save user message
        user_msg = AIMessage.objects.create(
            conversation=conversation,
            message_type='USER',
            content=user_message
        )
        
        # Get AI response
        ai_service = GeminiAIService()
        
        # Get conversation context
        context = list(conversation.messages.order_by('created_at').values('message_type', 'content'))
        context_list = [
            {'type': 'user' if msg['message_type'] == 'USER' else 'ai', 'content': msg['content']}
            for msg in context[:-1]  # Exclude the just-added message
        ]
        
        ai_response = ai_service.chat_response(user_message, context_list)
        
        # Save AI response
        ai_msg = AIMessage.objects.create(
            conversation=conversation,
            message_type='AI',
            content=ai_response
        )
        
        return JsonResponse({
            'success': True,
            'conversation_id': conversation.id,
            'user_message': user_message,
            'ai_response': ai_response,
            'timestamp': ai_msg.created_at.strftime('%I:%M %p')
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def conversation_list(request):
    """List all user conversations"""
    conversations = AIConversation.objects.filter(user=request.user)
    return render(request, 'ai_assistant/conversation_list.html', {'conversations': conversations})

@login_required
def conversation_delete(request, pk):
    """Delete a conversation"""
    conversation = get_object_or_404(AIConversation, pk=pk, user=request.user)
    
    if request.method == 'POST':
        conversation.delete()
        messages.success(request, 'Conversation deleted successfully!')
        return redirect('ai_assistant:conversation_list')
    
    return render(request, 'ai_assistant/conversation_confirm_delete.html', {'conversation': conversation})

@login_required
def generate_summary(request):
    """Generate AI summary of content"""
    if request.method == 'POST':
        form = AIPromptForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            course_id = form.cleaned_data.get('course')
            
            ai_service = GeminiAIService()
            summary = ai_service.generate_summary(content)
            
            # Save generated content
            AIGeneratedContent.objects.create(
                user=request.user,
                course_id=course_id,
                content_type='SUMMARY',
                prompt=content[:500],
                generated_content=summary
            )
            
            context = {
                'form': form,
                'summary': summary,
                'original_content': content
            }
            return render(request, 'ai_assistant/generate_summary.html', context)
    else:
        form = AIPromptForm()
    
    return render(request, 'ai_assistant/generate_summary.html', {'form': form})

@login_required
def generate_explanation(request):
    """Generate AI explanation of a topic"""
    if request.method == 'POST':
        topic = request.POST.get('topic', '').strip()
        level = request.POST.get('level', 'intermediate')
        course_id = request.POST.get('course')
        
        if topic:
            ai_service = GeminiAIService()
            explanation = ai_service.generate_explanation(topic, level)
            
            # Save generated content
            AIGeneratedContent.objects.create(
                user=request.user,
                course_id=course_id if course_id else None,
                content_type='EXPLANATION',
                prompt=f"{topic} (Level: {level})",
                generated_content=explanation
            )
            
            context = {
                'explanation': explanation,
                'topic': topic,
                'level': level
            }
            return render(request, 'ai_assistant/generate_explanation.html', context)
    
    return render(request, 'ai_assistant/generate_explanation.html')

@login_required
def generate_questions(request):
    """Generate practice questions"""
    if request.method == 'POST':
        topic = request.POST.get('topic', '').strip()
        count = int(request.POST.get('count', 5))
        course_id = request.POST.get('course')
        
        if topic:
            ai_service = GeminiAIService()
            questions = ai_service.generate_practice_questions(topic, count)
            
            # Save generated content
            AIGeneratedContent.objects.create(
                user=request.user,
                course_id=course_id if course_id else None,
                content_type='PRACTICE',
                prompt=f"{topic} ({count} questions)",
                generated_content=questions
            )
            
            context = {
                'questions': questions,
                'topic': topic,
                'count': count
            }
            return render(request, 'ai_assistant/generate_questions.html', context)
    
    return render(request, 'ai_assistant/generate_questions.html')

@login_required
def ai_history(request):
    """Display user's AI generation history"""
    history = AIGeneratedContent.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'ai_assistant/ai_history.html', {'history': history})
