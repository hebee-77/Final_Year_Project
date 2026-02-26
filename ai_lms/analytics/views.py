from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import StudentProgress, LearningActivity, EngagementMetrics
from content.models import Course
from accounts.models import User
from assessments.models import Submission
import json

@login_required
def student_progress(request):
    """Display student's overall progress"""
    if not request.user.is_student():
        messages.error(request, 'Only students can view progress.')
        return redirect('core:dashboard')
    
    # Get all progress records
    progress_records = StudentProgress.objects.filter(
        student=request.user
    ).select_related('course')
    
    # Calculate overall statistics
    total_courses = progress_records.count()
    avg_completion = progress_records.aggregate(
        Avg('completion_percentage')
    )['completion_percentage__avg'] or 0
    
    total_time = progress_records.aggregate(
        Sum('time_spent_minutes')
    )['time_spent_minutes__sum'] or 0
    
    # Recent activities
    recent_activities = LearningActivity.objects.filter(
        student=request.user
    ).select_related('course')[:20]
    
    # Prepare chart data for progress over time
    progress_data = []
    for record in progress_records:
        progress_data.append({
            'course': record.course.title,
            'completion': round(record.completion_percentage, 1)
        })
    
    context = {
        'progress_records': progress_records,
        'total_courses': total_courses,
        'avg_completion': round(avg_completion, 1),
        'total_time': total_time,
        'recent_activities': recent_activities,
        'progress_data_json': json.dumps(progress_data),
    }
    return render(request, 'analytics/student_progress.html', context)

@login_required
def course_progress_detail(request, course_pk):
    """Detailed progress for a specific course"""
    if not request.user.is_student():
        messages.error(request, 'Only students can view progress.')
        return redirect('core:dashboard')
    
    course = get_object_or_404(Course, pk=course_pk)
    
    # Check enrollment
    if not request.user.enrolled_courses.filter(pk=course_pk).exists():
        messages.error(request, 'You are not enrolled in this course.')
        return redirect('content:course_detail', pk=course_pk)
    
    # Get progress record
    progress = StudentProgress.objects.filter(
        student=request.user,
        course=course
    ).first()
    
    # Get course materials
    materials = course.materials.all()
    
    # Get assignments and submissions
    assignments = course.assignments.filter(status='PUBLISHED')
    submissions = Submission.objects.filter(
        assignment__course=course,
        student=request.user
    )
    
    # Calculate assignment completion rate
    assignment_completion = 0
    if assignments.count() > 0:
        assignment_completion = (submissions.count() / assignments.count()) * 100
    
    # Get course activities
    activities = LearningActivity.objects.filter(
        student=request.user,
        course=course
    ).order_by('-timestamp')[:15]
    
    context = {
        'course': course,
        'progress': progress,
        'materials': materials,
        'assignments': assignments,
        'submissions': submissions,
        'assignment_completion': round(assignment_completion, 1),
        'activities': activities,
    }
    return render(request, 'analytics/course_progress_detail.html', context)

@login_required
def activity_log(request):
    """Display student's activity log"""
    if not request.user.is_student():
        messages.error(request, 'Only students can view activity log.')
        return redirect('core:dashboard')
    
    # Get filter parameters
    activity_type = request.GET.get('type', '')
    course_id = request.GET.get('course', '')
    
    # Base query
    activities = LearningActivity.objects.filter(
        student=request.user
    ).select_related('course')
    
    # Apply filters
    if activity_type:
        activities = activities.filter(activity_type=activity_type)
    if course_id:
        activities = activities.filter(course_id=course_id)
    
    # Get user's courses for filter dropdown
    courses = request.user.enrolled_courses.all()
    
    # Paginate
    from django.core.paginator import Paginator
    paginator = Paginator(activities, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'courses': courses,
        'selected_type': activity_type,
        'selected_course': course_id,
        'activity_types': LearningActivity.ActivityType.choices,
    }
    return render(request, 'analytics/activity_log.html', context)

@login_required
def class_analytics(request, course_pk):
    """Teacher view of class analytics"""
    if not request.user.is_teacher():
        messages.error(request, 'Only teachers can view class analytics.')
        return redirect('core:dashboard')
    
    course = get_object_or_404(Course, pk=course_pk, teacher=request.user)
    
    # Get enrolled students
    students = course.enrolled_students.all()
    
    # Get student progress
    progress_records = StudentProgress.objects.filter(
        course=course
    ).select_related('student')
    
    # Calculate class statistics
    class_stats = {
        'total_students': students.count(),
        'avg_progress': progress_records.aggregate(
            Avg('completion_percentage')
        )['completion_percentage__avg'] or 0,
        'materials_count': course.materials.count(),
        'assignments_count': course.assignments.count(),
    }
    
    # Get submission statistics
    assignments = course.assignments.filter(status='PUBLISHED')
    total_expected_submissions = assignments.count() * students.count()
    actual_submissions = Submission.objects.filter(
        assignment__course=course
    ).count()
    
    submission_rate = 0
    if total_expected_submissions > 0:
        submission_rate = (actual_submissions / total_expected_submissions) * 100
    
    # Get top performers
    top_performers = progress_records.order_by('-completion_percentage')[:5]
    
    # Get struggling students (below 50% completion)
    struggling_students = progress_records.filter(
        completion_percentage__lt=50
    )
    
    # Prepare chart data
    progress_distribution = {
        '0-25%': progress_records.filter(completion_percentage__lt=25).count(),
        '25-50%': progress_records.filter(
            completion_percentage__gte=25,
            completion_percentage__lt=50
        ).count(),
        '50-75%': progress_records.filter(
            completion_percentage__gte=50,
            completion_percentage__lt=75
        ).count(),
        '75-100%': progress_records.filter(completion_percentage__gte=75).count(),
    }
    
    context = {
        'course': course,
        'class_stats': class_stats,
        'submission_rate': round(submission_rate, 1),
        'top_performers': top_performers,
        'struggling_students': struggling_students,
        'progress_distribution': json.dumps(progress_distribution),
    }
    return render(request, 'analytics/class_analytics.html', context)

@login_required
def student_performance(request, student_pk):
    """Teacher view of individual student performance"""
    if not request.user.is_teacher():
        messages.error(request, 'Only teachers can view student performance.')
        return redirect('core:dashboard')
    
    student = get_object_or_404(User, pk=student_pk, role=User.Role.STUDENT)
    
    # Get courses taught by teacher that student is enrolled in
    common_courses = Course.objects.filter(
        teacher=request.user,
        enrolled_students=student
    )
    
    if not common_courses.exists():
        messages.error(request, 'This student is not enrolled in your courses.')
        return redirect('core:dashboard')
    
    # Get progress in all common courses
    progress_records = StudentProgress.objects.filter(
        student=student,
        course__in=common_courses
    ).select_related('course')
    
    # Get submissions
    submissions = Submission.objects.filter(
        student=student,
        assignment__course__in=common_courses
    ).select_related('assignment')
    
    # Calculate average grade
    graded_submissions = submissions.filter(status='GRADED', score__isnull=False)
    avg_grade = graded_submissions.aggregate(Avg('score'))['score__avg'] or 0
    
    # Get recent activities
    activities = LearningActivity.objects.filter(
        student=student,
        course__in=common_courses
    ).order_by('-timestamp')[:20]
    
    context = {
        'student': student,
        'common_courses': common_courses,
        'progress_records': progress_records,
        'submissions': submissions,
        'avg_grade': round(avg_grade, 1),
        'activities': activities,
    }
    return render(request, 'analytics/student_performance.html', context)

@login_required
def system_analytics(request):
    """Admin view of system-wide analytics"""
    if not request.user.is_admin():
        messages.error(request, 'Only admins can view system analytics.')
        return redirect('core:dashboard')
    
    # User statistics
    total_users = User.objects.count()
    total_students = User.objects.filter(role=User.Role.STUDENT).count()
    total_teachers = User.objects.filter(role=User.Role.TEACHER).count()
    
    # Course statistics
    total_courses = Course.objects.count()
    active_courses = Course.objects.filter(is_active=True).count()
    
    # Content statistics
    from content.models import LearningMaterial, Subject
    total_materials = LearningMaterial.objects.count()
    total_subjects = Subject.objects.count()
    
    # Assignment statistics
    from assessments.models import Assignment
    total_assignments = Assignment.objects.count()
    total_submissions = Submission.objects.count()
    
    # Engagement statistics
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    weekly_activities = LearningActivity.objects.filter(
        timestamp__date__gte=week_ago
    ).count()
    
    # Get recent registrations
    recent_users = User.objects.order_by('-created_at')[:10]
    
    # Course enrollment distribution
    course_enrollments = Course.objects.annotate(
        student_count=Count('enrolled_students')
    ).order_by('-student_count')[:10]
    
    # AI usage statistics
    from ai_assistant.models import AIConversation, AIGeneratedContent
    total_ai_conversations = AIConversation.objects.count()
    total_ai_generations = AIGeneratedContent.objects.count()
    
    # Prepare chart data
    user_distribution = {
        'Students': total_students,
        'Teachers': total_teachers,
        'Admins': total_users - total_students - total_teachers
    }
    
    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_courses': total_courses,
        'active_courses': active_courses,
        'total_materials': total_materials,
        'total_subjects': total_subjects,
        'total_assignments': total_assignments,
        'total_submissions': total_submissions,
        'weekly_activities': weekly_activities,
        'recent_users': recent_users,
        'course_enrollments': course_enrollments,
        'total_ai_conversations': total_ai_conversations,
        'total_ai_generations': total_ai_generations,
        'user_distribution': json.dumps(user_distribution),
    }
    return render(request, 'analytics/system_analytics.html', context)

@login_required
def engagement_metrics(request):
    """Admin view of engagement metrics"""
    if not request.user.is_admin():
        messages.error(request, 'Only admins can view engagement metrics.')
        return redirect('core:dashboard')
    
    # Date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Get daily metrics
    daily_metrics = EngagementMetrics.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).values('date').annotate(
        total_users=Count('user', distinct=True),
        total_time=Sum('total_time_minutes'),
        total_materials=Sum('materials_viewed'),
        total_ai=Sum('ai_interactions'),
        total_assignments=Sum('assignments_submitted')
    ).order_by('date')
    
    # Prepare chart data
    dates = []
    active_users = []
    ai_interactions = []
    
    for metric in daily_metrics:
        dates.append(metric['date'].strftime('%Y-%m-%d'))
        active_users.append(metric['total_users'])
        ai_interactions.append(metric['total_ai'])
    
    chart_data = {
        'dates': dates,
        'active_users': active_users,
        'ai_interactions': ai_interactions
    }
    
    # Calculate trends
    total_engagement_time = sum(m['total_time'] or 0 for m in daily_metrics)
    avg_daily_users = sum(m['total_users'] for m in daily_metrics) / len(daily_metrics) if daily_metrics else 0
    
    context = {
        'daily_metrics': daily_metrics,
        'chart_data': json.dumps(chart_data),
        'total_engagement_time': total_engagement_time,
        'avg_daily_users': round(avg_daily_users, 1),
        'date_range': f"{start_date} to {end_date}",
    }
    return render(request, 'analytics/engagement_metrics.html', context)
