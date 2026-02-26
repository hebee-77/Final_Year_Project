from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Assignment, Submission, AIFeedback, TeacherFeedback
from .forms import AssignmentForm, SubmissionForm, GradeForm, TeacherFeedbackForm
from ai_assistant.services import GeminiAIService
from analytics.models import LearningActivity


@login_required
def assignment_list(request):
    """List assignments based on user role"""
    user = request.user
    
    if user.is_student:
        # Get assignments from enrolled courses
        assignments = Assignment.objects.filter(
            course__enrolled_students=user,
            status='PUBLISHED'
        ).order_by('-due_date')
        
        # Check submission status
        for assignment in assignments:
            assignment.user_submitted = Submission.objects.filter(
                assignment=assignment,
                student=user
            ).exists()
    elif user.is_teacher:
        assignments = Assignment.objects.filter(
            course__teacher=user
        ).order_by('-created_at')
    else:
        assignments = Assignment.objects.all().order_by('-created_at')
    
    context = {'assignments': assignments}
    return render(request, 'assessments/assignment_list.html', context)


@login_required
def assignment_detail(request, pk):
    """Display assignment details"""
    assignment = get_object_or_404(Assignment, pk=pk)
    user = request.user
    
    # Debug logging
    print(f"\n=== Assignment Detail Debug ===")
    print(f"User: {user.username}")
    print(f"User Role: {user.role}")
    print(f"Is Student: {user.is_student}")
    print(f"Is Teacher: {user.is_teacher}")
    print(f"Is Admin: {user.is_admin}")
    print(f"Assignment: {assignment.title}")
    print(f"Assignment Course: {assignment.course.title}")
    print(f"Course Teacher: {assignment.course.teacher.username}")
    print(f"Total Submissions: {assignment.submissions.count()}")
    
    # Check if student has submitted
    user_submission = None
    if user.is_student:
        user_submission = Submission.objects.filter(
            assignment=assignment,
            student=user
        ).first()
        print(f"User has submitted: {user_submission is not None}")
    
    # Get all submissions - for both teacher and admin
    show_submissions = False
    if user.is_teacher or user.is_admin:
        # Teachers can see their own assignments, admins can see all
        if assignment.course.teacher == user or user.is_admin:
            show_submissions = True
            print(f"Show submissions: True")
        else:
            print(f"Show submissions: False (not the course teacher)")
    
    print(f"=== End Debug ===\n")
    
    context = {
        'assignment': assignment,
        'user_submission': user_submission,
        'show_submissions': show_submissions,
    }
    return render(request, 'assessments/assignment_detail.html', context)


@login_required
def assignment_create(request):
    """Create new assignment (teachers only)"""
    if not request.user.is_teacher:
        messages.error(request, 'Only teachers can create assignments.')
        return redirect('assessments:assignment_list')
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, teacher=request.user)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.save()
            messages.success(request, 'Assignment created successfully!')
            return redirect('assessments:assignment_detail', pk=assignment.pk)
    else:
        form = AssignmentForm(teacher=request.user)
    
    return render(request, 'assessments/assignment_form.html', {'form': form, 'action': 'Create'})


@login_required
def assignment_edit(request, pk):
    """Edit assignment"""
    assignment = get_object_or_404(Assignment, pk=pk)
    
    if not (request.user == assignment.course.teacher or request.user.is_admin):
        messages.error(request, 'You do not have permission to edit this assignment.')
        return redirect('assessments:assignment_detail', pk=pk)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment, teacher=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment updated successfully!')
            return redirect('assessments:assignment_detail', pk=pk)
    else:
        form = AssignmentForm(instance=assignment, teacher=request.user)
    
    return render(request, 'assessments/assignment_form.html', {
        'form': form,
        'action': 'Edit',
        'assignment': assignment
    })


@login_required
def assignment_delete(request, pk):
    """Delete assignment"""
    assignment = get_object_or_404(Assignment, pk=pk)
    
    if not (request.user == assignment.course.teacher or request.user.is_admin):
        messages.error(request, 'You do not have permission to delete this assignment.')
        return redirect('assessments:assignment_detail', pk=pk)
    
    if request.method == 'POST':
        course_pk = assignment.course.pk
        assignment.delete()
        messages.success(request, 'Assignment deleted successfully!')
        return redirect('content:course_detail', pk=course_pk)
    
    return render(request, 'assessments/assignment_confirm_delete.html', {'assignment': assignment})


@login_required
def submit_assignment(request, assignment_pk):
    """Submit assignment - Main submission view"""
    if not request.user.is_student:
        messages.error(request, 'Only students can submit assignments.')
        return redirect('assessments:assignment_list')
    
    assignment = get_object_or_404(Assignment, pk=assignment_pk)
    
    # Check if enrolled
    if not assignment.course.enrolled_students.filter(pk=request.user.pk).exists():
        messages.error(request, 'You are not enrolled in this course.')
        return redirect('content:course_list')
    
    # Check if already submitted
    existing_submission = Submission.objects.filter(
        assignment=assignment, 
        student=request.user
    ).first()
    
    if existing_submission:
        messages.warning(request, 'You have already submitted this assignment.')
        return redirect('assessments:submission_detail', pk=existing_submission.pk)
    
    # Check due date (warning only, still allow submission)
    if timezone.now() > assignment.due_date:
        messages.warning(request, 'Note: This assignment is past the due date. Late submissions may be penalized.')
    
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.status = 'SUBMITTED'
            submission.save()
            
            # Log activity
            try:
                LearningActivity.objects.create(
                    student=request.user,
                    course=assignment.course,
                    activity_type='ASSIGNMENT_SUBMIT',
                    description=f'Submitted: {assignment.title}'
                )
            except:
                pass  # Continue even if activity logging fails
            
            messages.success(request, 'Assignment submitted successfully!')
            return redirect('assessments:submission_detail', pk=submission.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SubmissionForm()
    
    context = {
        'form': form,
        'assignment': assignment,
    }
    return render(request, 'assessments/submit_assignment.html', context)


# Alias for backward compatibility
submission_create = submit_assignment


@login_required
def submission_detail(request, pk):
    """View submission details"""
    submission = get_object_or_404(Submission, pk=pk)
    
    # Debug
    print(f"\n=== Submission Detail Debug ===")
    print(f"User: {request.user.username}, Role: {request.user.role}")
    print(f"Submission Student: {submission.student.username}")
    print(f"Assignment: {submission.assignment.title}")
    print(f"Course: {submission.assignment.course.title}")
    print(f"Course Teacher: {submission.assignment.course.teacher.username}")
    print(f"Is Student: {request.user.is_student}")
    print(f"Is Teacher: {request.user.is_teacher}")
    print(f"Is Admin: {request.user.is_admin}")
    
    # Check permissions
    can_view = False
    
    if request.user.is_student:
        # Students can only view their own submissions
        if submission.student == request.user:
            can_view = True
            print("Access granted: Student viewing own submission")
        else:
            print("Access denied: Student trying to view another student's submission")
    
    elif request.user.is_teacher:
        # Teachers can view submissions from their courses
        if submission.assignment.course.teacher == request.user:
            can_view = True
            print("Access granted: Teacher viewing submission from their course")
        else:
            print("Access denied: Teacher trying to view submission from another teacher's course")
    
    elif request.user.is_admin:
        # Admins can view all submissions
        can_view = True
        print("Access granted: Admin viewing submission")
    
    print(f"Can view: {can_view}")
    print(f"=== End Debug ===\n")
    
    if not can_view:
        messages.error(request, 'You do not have permission to view this submission.')
        return redirect('assessments:assignment_list')
    
    # Get teacher feedback
    teacher_feedbacks = submission.teacher_feedback_set.all()
    
    # Get AI feedback if exists
    ai_feedback = None
    try:
        ai_feedback = submission.ai_feedback
    except:
        pass
    
    context = {
        'submission': submission,
        'assignment': submission.assignment,
        'teacher_feedbacks': teacher_feedbacks,
        'ai_feedback': ai_feedback,
    }
    return render(request, 'assessments/submission_detail.html', context)


@login_required
def submission_list(request):
    """List all submissions for grading (teachers)"""
    if not (request.user.is_teacher or request.user.is_admin):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    # Debug output
    print(f"\n=== Submission List Debug ===")
    print(f"User: {request.user.username}")
    print(f"Is Teacher: {request.user.is_teacher}")
    print(f"Is Admin: {request.user.is_admin}")
    
    if request.user.is_teacher:
        submissions = Submission.objects.filter(
            assignment__course__teacher=request.user
        ).select_related('assignment', 'student', 'assignment__course').order_by('-submitted_at')
        print(f"Teacher submissions count: {submissions.count()}")
    else:
        submissions = Submission.objects.all().select_related(
            'assignment', 'student', 'assignment__course'
        ).order_by('-submitted_at')
        print(f"Admin submissions count: {submissions.count()}")
    
    print(f"Submissions list: {list(submissions)}")
    print(f"=== End Debug ===\n")
    
    context = {'submissions': submissions}
    return render(request, 'assessments/submission_list.html', context)


@login_required
def grade_submission(request, pk):
    """Grade student submission"""
    submission = get_object_or_404(Submission, pk=pk)
    
    if not (request.user == submission.assignment.course.teacher or request.user.is_admin):
        messages.error(request, 'You do not have permission to grade this submission.')
        return redirect('assessments:submission_detail', pk=pk)
    
    if request.method == 'POST':
        grade_form = GradeForm(request.POST, instance=submission)
        feedback_form = TeacherFeedbackForm(request.POST)
        
        if grade_form.is_valid() and feedback_form.is_valid():
            submission = grade_form.save(commit=False)
            submission.status = 'GRADED'
            submission.graded_at = timezone.now()
            submission.save()
            
            # Save teacher feedback
            feedback_text = feedback_form.cleaned_data.get('feedback_text')
            if feedback_text:
                TeacherFeedback.objects.update_or_create(
                    submission=submission,
                    teacher=request.user,
                    defaults={'feedback_text': feedback_text}
                )
            
            messages.success(request, 'Submission graded successfully!')
            return redirect('assessments:submission_detail', pk=pk)
    else:
        grade_form = GradeForm(instance=submission)
        
        # Pre-populate feedback if exists
        teacher_feedback = TeacherFeedback.objects.filter(
            submission=submission,
            teacher=request.user
        ).first()
        feedback_form = TeacherFeedbackForm(
            initial={'feedback_text': teacher_feedback.feedback_text if teacher_feedback else ''}
        )
    
    context = {
        'submission': submission,
        'grade_form': grade_form,
        'feedback_form': feedback_form,
    }
    return render(request, 'assessments/submission_grade.html', context)


# Alias for backward compatibility
submission_grade = grade_submission


@login_required
def generate_ai_feedback(request, pk):
    """Generate AI feedback for submission"""
    submission = get_object_or_404(Submission, pk=pk)
    
    # Check permissions
    can_access = False
    
    if request.user.is_student:
        if request.user == submission.student:
            can_access = True
    elif request.user.is_teacher:
        if request.user == submission.assignment.course.teacher:
            can_access = True
    elif request.user.is_admin:
        can_access = True
    
    if not can_access:
        messages.error(request, 'You do not have permission to view this feedback.')
        return redirect('assessments:assignment_list')
    
    # Check if feedback already exists
    ai_feedback = AIFeedback.objects.filter(submission=submission).first()
    
    if not ai_feedback:
        try:
            # Generate AI feedback
            ai_service = GeminiAIService()
            feedback_data = ai_service.provide_feedback(
                submission.assignment.description,
                submission.content
            )
            
            ai_feedback = AIFeedback.objects.create(
                submission=submission,
                feedback_text=f"Strengths:\n{feedback_data.get('strengths', '')}\n\nAreas for Improvement:\n{feedback_data.get('improvements', '')}\n\nSuggestions:\n{feedback_data.get('suggestions', '')}",
                strengths=feedback_data.get('strengths', ''),
                improvements=feedback_data.get('improvements', ''),
                suggestions=feedback_data.get('suggestions', '')
            )
            
            messages.success(request, 'AI feedback generated successfully!')
        except Exception as e:
            messages.error(request, f'Error generating AI feedback: {str(e)}')
            return redirect('assessments:submission_detail', pk=pk)
    
    context = {
        'submission': submission,
        'ai_feedback': ai_feedback,
    }
    return render(request, 'assessments/ai_feedback.html', context)


@login_required
def ai_feedback_view(request, pk):
    """View AI feedback (alias for generate_ai_feedback)"""
    return generate_ai_feedback(request, pk)
