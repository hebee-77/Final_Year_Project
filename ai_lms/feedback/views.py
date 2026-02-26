from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SystemFeedback, SatisfactionSurvey
from .forms import SystemFeedbackForm, SatisfactionSurveyForm
from content.models import Course


@login_required
def feedback_submit(request):
    """Submit system feedback"""
    if request.method == 'POST':
        form = SystemFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('feedback:my_feedback')
    else:
        form = SystemFeedbackForm()
    
    context = {'form': form}
    return render(request, 'feedback/feedback_submit.html', context)


@login_required
def my_feedback(request):
    """View user's own feedback"""
    feedbacks = SystemFeedback.objects.filter(user=request.user).order_by('-created_at')
    context = {'feedbacks': feedbacks}
    return render(request, 'feedback/my_feedback.html', context)


@login_required
def feedback_manage(request):
    """Admin view to manage all feedback"""
    if not request.user.is_admin:
        messages.error(request, 'Only admins can manage feedback.')
        return redirect('core:dashboard')
    
    all_feedback = SystemFeedback.objects.all().select_related('user').order_by('-created_at')
    
    context = {'all_feedback': all_feedback}
    return render(request, 'feedback/feedback_manage.html', context)


@login_required
def feedback_review(request, pk):
    """Admin review and respond to feedback"""
    if not request.user.is_admin:
        messages.error(request, 'Only admins can review feedback.')
        return redirect('core:dashboard')
    
    feedback = get_object_or_404(SystemFeedback, pk=pk)
    
    if request.method == 'POST':
        feedback.status = request.POST.get('status')
        feedback.admin_response = request.POST.get('admin_response')
        feedback.save()
        messages.success(request, 'Feedback updated successfully!')
        return redirect('feedback:feedback_manage')
    
    context = {'feedback': feedback}
    return render(request, 'feedback/feedback_review.html', context)


@login_required
def survey_create(request, course_pk):
    """Create satisfaction survey for a course"""
    if not request.user.is_student:
        messages.error(request, 'Only students can submit surveys.')
        return redirect('content:course_list')
    
    course = get_object_or_404(Course, pk=course_pk)
    
    # Check if already submitted
    existing_survey = SatisfactionSurvey.objects.filter(
        student=request.user,
        course=course
    ).first()
    
    if existing_survey:
        messages.warning(request, 'You have already submitted a survey for this course.')
        return redirect('content:course_detail', pk=course_pk)
    
    if request.method == 'POST':
        form = SatisfactionSurveyForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.student = request.user
            survey.course = course
            survey.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('content:course_detail', pk=course_pk)
    else:
        form = SatisfactionSurveyForm()
    
    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'feedback/survey_create.html', context)


@login_required
def survey_list(request):
    """View all surveys (Admin/Teacher)"""
    if request.user.is_admin:
        surveys = SatisfactionSurvey.objects.all().select_related('student', 'course')
    elif request.user.is_teacher:
        surveys = SatisfactionSurvey.objects.filter(
            course__teacher=request.user
        ).select_related('student', 'course')
    else:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    context = {'surveys': surveys}
    return render(request, 'feedback/survey_list.html', context)
