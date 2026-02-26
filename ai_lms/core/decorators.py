from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def student_required(view_func):
    """Decorator to require student role"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_student():
            messages.error(request, 'This page is only accessible to students.')
            return redirect('core:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

def teacher_required(view_func):
    """Decorator to require teacher role"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_teacher():
            messages.error(request, 'This page is only accessible to teachers.')
            return redirect('core:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_required(view_func):
    """Decorator to require admin role"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_admin():
            messages.error(request, 'This page is only accessible to administrators.')
            return redirect('core:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

def teacher_or_admin_required(view_func):
    """Decorator to require teacher or admin role"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not (request.user.is_teacher() or request.user.is_admin()):
            messages.error(request, 'This page is only accessible to teachers and administrators.')
            return redirect('core:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
