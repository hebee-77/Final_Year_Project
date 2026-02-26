from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, StudentProfile, TeacherProfile
from .forms import UserRegistrationForm, ProfileEditForm

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create profile based on role
            if user.role == User.Role.STUDENT:
                StudentProfile.objects.create(
                    user=user,
                    student_id=f"STU{user.id:06d}"
                )
            elif user.role == User.Role.TEACHER:
                TeacherProfile.objects.create(
                    user=user,
                    employee_id=f"EMP{user.id:06d}",
                    department="General"
                )
            
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('core:dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def logout_view(request):
    """Custom logout view that handles both GET and POST"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:home')

@login_required
def profile(request):
    """User profile view"""
    return render(request, 'accounts/profile.html')

@login_required
def edit_profile(request):
    """Edit user profile"""
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})
