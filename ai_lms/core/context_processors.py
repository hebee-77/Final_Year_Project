from content.models import Course
from assessments.models import Assignment

def site_context(request):
    """Add common context variables to all templates"""
    context = {}
    
    if request.user.is_authenticated:
        if request.user.is_student():
            # Count pending assignments for students
            context['pending_assignments_count'] = Assignment.objects.filter(
                course__enrolled_students=request.user,
                status='PUBLISHED'
            ).exclude(submissions__student=request.user).count()
            
        elif request.user.is_teacher():
            # Count pending reviews for teachers
            from assessments.models import Submission
            context['pending_reviews_count'] = Submission.objects.filter(
                assignment__course__teacher=request.user,
                status='SUBMITTED'
            ).count()
    
    return context
