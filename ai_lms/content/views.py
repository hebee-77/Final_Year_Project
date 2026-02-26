from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Course, LearningMaterial, LearningGoal, Subject
from .forms import CourseForm, LearningMaterialForm, LearningGoalForm, SubjectForm
from analytics.models import LearningActivity, StudentProgress

@login_required
def course_list(request):
    """Display list of courses based on user role"""
    user = request.user
    search_query = request.GET.get('search', '')
    
    if user.is_student():
        courses = Course.objects.filter(is_active=True)
        enrolled_courses = user.enrolled_courses.all()
    elif user.is_teacher():
        courses = user.courses_teaching.all()
        enrolled_courses = None
    else:
        courses = Course.objects.all()
        enrolled_courses = None
    
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    context = {
        'courses': courses,
        'enrolled_courses': enrolled_courses,
        'search_query': search_query,
    }
    return render(request, 'content/course_list.html', context)

@login_required
def course_detail(request, pk):
    """Display course details"""
    course = get_object_or_404(Course, pk=pk)
    user = request.user
    
    # Check if student is enrolled
    is_enrolled = user.is_student() and user.enrolled_courses.filter(pk=pk).exists()
    
    # Get course materials
    materials = course.materials.all()
    
    # Get assignments
    assignments = course.assignments.filter(status='PUBLISHED')
    
    # Get student progress if enrolled
    progress = None
    if is_enrolled:
        progress, created = StudentProgress.objects.get_or_create(
            student=user,
            course=course,
            defaults={'total_materials': materials.count()}
        )
    
    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'materials': materials,
        'assignments': assignments,
        'progress': progress,
    }
    return render(request, 'content/course_detail.html', context)

@login_required
def course_enroll(request, pk):
    """Enroll student in a course"""
    if not request.user.is_student():
        messages.error(request, 'Only students can enroll in courses.')
        return redirect('content:course_list')
    
    course = get_object_or_404(Course, pk=pk, is_active=True)
    
    if request.user.enrolled_courses.filter(pk=pk).exists():
        messages.warning(request, 'You are already enrolled in this course.')
    else:
        course.enrolled_students.add(request.user)
        
        # Create progress record
        StudentProgress.objects.create(
            student=request.user,
            course=course,
            total_materials=course.materials.count()
        )
        
        # Log activity
        LearningActivity.objects.create(
            student=request.user,
            course=course,
            activity_type='MATERIAL_VIEW',
            description=f'Enrolled in {course.title}'
        )
        
        messages.success(request, f'Successfully enrolled in {course.title}!')
    
    return redirect('content:course_detail', pk=pk)

@login_required
def course_create(request):
    """Create new course (teachers and admins only)"""
    if not (request.user.is_teacher() or request.user.is_admin()):
        messages.error(request, 'You do not have permission to create courses.')
        return redirect('content:course_list')
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            if request.user.is_teacher():
                course.teacher = request.user
            course.save()
            messages.success(request, 'Course created successfully!')
            return redirect('content:course_detail', pk=course.pk)
    else:
        form = CourseForm()
    
    return render(request, 'content/course_form.html', {'form': form, 'action': 'Create'})

@login_required
def course_edit(request, pk):
    """Edit existing course"""
    course = get_object_or_404(Course, pk=pk)
    
    if not (request.user == course.teacher or request.user.is_admin()):
        messages.error(request, 'You do not have permission to edit this course.')
        return redirect('content:course_detail', pk=pk)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('content:course_detail', pk=pk)
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'content/course_form.html', {'form': form, 'action': 'Edit', 'course': course})

@login_required
def material_detail(request, pk):
    """Display learning material details"""
    material = get_object_or_404(LearningMaterial, pk=pk)
    course = material.course
    
    # Check if user has access
    if request.user.is_student():
        if not request.user.enrolled_courses.filter(pk=course.pk).exists():
            messages.error(request, 'You must be enrolled to view this material.')
            return redirect('content:course_detail', pk=course.pk)
        
        # Log activity
        LearningActivity.objects.create(
            student=request.user,
            course=course,
            activity_type='MATERIAL_VIEW',
            description=f'Viewed: {material.title}'
        )
        
        # Update progress
        progress = StudentProgress.objects.filter(student=request.user, course=course).first()
        if progress:
            progress.materials_completed += 1
            progress.completion_percentage = (progress.materials_completed / progress.total_materials) * 100
            progress.save()
    
    context = {
        'material': material,
        'course': course,
    }
    return render(request, 'content/material_detail.html', context)

@login_required
def material_create(request, course_pk):
    """Create learning material for a course"""
    course = get_object_or_404(Course, pk=course_pk)
    
    if not (request.user == course.teacher or request.user.is_admin()):
        messages.error(request, 'You do not have permission to add materials.')
        return redirect('content:course_detail', pk=course_pk)
    
    if request.method == 'POST':
        form = LearningMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course
            material.uploaded_by = request.user
            material.save()
            
            # Update total materials for all enrolled students
            StudentProgress.objects.filter(course=course).update(total_materials=course.materials.count())
            
            messages.success(request, 'Learning material added successfully!')
            return redirect('content:course_detail', pk=course_pk)
    else:
        form = LearningMaterialForm()
    
    return render(request, 'content/material_form.html', {'form': form, 'course': course})

@login_required
def material_edit(request, pk):
    """Edit learning material"""
    material = get_object_or_404(LearningMaterial, pk=pk)
    
    if not (request.user == material.course.teacher or request.user.is_admin()):
        messages.error(request, 'You do not have permission to edit this material.')
        return redirect('content:material_detail', pk=pk)
    
    if request.method == 'POST':
        form = LearningMaterialForm(request.POST, request.FILES, instance=material)
        if form.is_valid():
            form.save()
            messages.success(request, 'Material updated successfully!')
            return redirect('content:material_detail', pk=pk)
    else:
        form = LearningMaterialForm(instance=material)
    
    return render(request, 'content/material_form.html', {'form': form, 'material': material})

@login_required
def material_delete(request, pk):
    """Delete learning material"""
    material = get_object_or_404(LearningMaterial, pk=pk)
    course_pk = material.course.pk
    
    if not (request.user == material.course.teacher or request.user.is_admin()):
        messages.error(request, 'You do not have permission to delete this material.')
        return redirect('content:material_detail', pk=pk)
    
    if request.method == 'POST':
        material.delete()
        messages.success(request, 'Material deleted successfully!')
        return redirect('content:course_detail', pk=course_pk)
    
    return render(request, 'content/material_confirm_delete.html', {'material': material})

@login_required
def goal_list(request):
    """Display student's learning goals"""
    if not request.user.is_student():
        messages.error(request, 'Only students can view learning goals.')
        return redirect('core:dashboard')
    
    goals = LearningGoal.objects.filter(student=request.user).select_related('course')
    
    context = {
        'active_goals': goals.filter(is_completed=False),
        'completed_goals': goals.filter(is_completed=True),
    }
    return render(request, 'content/goal_list.html', context)

@login_required
def goal_create(request):
    """Create new learning goal"""
    if not request.user.is_student():
        messages.error(request, 'Only students can create learning goals.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = LearningGoalForm(request.POST, user=request.user)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.student = request.user
            goal.save()
            
            # Log activity
            LearningActivity.objects.create(
                student=request.user,
                course=goal.course,
                activity_type='GOAL_SET',
                description=f'Set goal: {goal.goal_text[:50]}'
            )
            
            messages.success(request, 'Learning goal created successfully!')
            return redirect('content:goal_list')
    else:
        form = LearningGoalForm(user=request.user)
    
    return render(request, 'content/goal_form.html', {'form': form})

@login_required
def goal_complete(request, pk):
    """Mark goal as completed"""
    goal = get_object_or_404(LearningGoal, pk=pk, student=request.user)
    
    if request.method == 'POST':
        from django.utils import timezone
        goal.is_completed = True
        goal.completed_date = timezone.now().date()
        goal.save()
        
        # Log activity
        LearningActivity.objects.create(
            student=request.user,
            course=goal.course,
            activity_type='GOAL_COMPLETE',
            description=f'Completed goal: {goal.goal_text[:50]}'
        )
        
        messages.success(request, 'Congratulations on completing your goal!')
        return redirect('content:goal_list')
    
    return render(request, 'content/goal_confirm_complete.html', {'goal': goal})

@login_required
def subject_list(request):
    """Display all subjects"""
    subjects = Subject.objects.all()
    return render(request, 'content/subject_list.html', {'subjects': subjects})

@login_required
def subject_create(request):
    """Create new subject (admin only)"""
    if not request.user.is_admin():
        messages.error(request, 'Only admins can create subjects.')
        return redirect('content:subject_list')
    
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.created_by = request.user
            subject.save()
            messages.success(request, 'Subject created successfully!')
            return redirect('content:subject_list')
    else:
        form = SubjectForm()
    
    return render(request, 'content/subject_form.html', {'form': form})
