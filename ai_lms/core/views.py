from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from content.models import Course
from assessments.models import Assignment, Submission
from analytics.models import StudentProgress
from accounts.models import User

def home(request):
    """Homepage view"""
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    """Role-based dashboard"""
    user = request.user
    context = {}
    
    if user.is_student():
        # Student dashboard data
        context['enrolled_courses'] = user.enrolled_courses.all()
        context['pending_assignments'] = Assignment.objects.filter(
            course__enrolled_students=user,
            status='PUBLISHED'
        ).exclude(submissions__student=user)[:5]
        context['recent_progress'] = StudentProgress.objects.filter(
            student=user
        ).order_by('-updated_at')[:5]
        
    elif user.is_teacher():
        # Teacher dashboard data
        context['courses_teaching'] = user.courses_teaching.all()
        context['pending_reviews'] = Submission.objects.filter(
            assignment__course__teacher=user,
            status='SUBMITTED'
        )[:10]
        
    elif user.is_admin():
        # Admin dashboard data
        context['total_students'] = User.objects.filter(role='STUDENT').count()
        context['total_teachers'] = User.objects.filter(role='TEACHER').count()
        context['total_courses'] = Course.objects.count()
    
    return render(request, 'core/dashboard.html', context)
