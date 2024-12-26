from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from .models import Task
from .forms import TaskForm
from .ai_utils import get_task_priority
from django.db.models import Count


def register(request):
    """Handles user registration."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def user_login(request):
    """Handles user login."""
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('task_list')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


@login_required
def user_logout(request):
    """Handles user logout."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


@login_required
def task_list(request):
    """Displays the list of tasks for the logged-in user."""
    tasks = Task.objects.filter(user=request.user)
    
    # Basic analytics
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(completed=True).count()
    pending_tasks = total_tasks - completed_tasks
    priority_breakdown = tasks.values('ai_priority').annotate(count=Count('ai_priority'))
    
    context = {
        'tasks': tasks,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'priority_breakdown': priority_breakdown,
    }
    return render(request, 'todos/task_list.html', context)


@login_required
def task_create(request):
    """Creates a new task."""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            
            # Get AI priority suggestion
            priority_data = get_task_priority(task.title, task.description, task.deadline)
            task.ai_priority = priority_data['priority']
            task.ai_score = priority_data['score']
            
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'todos/task_form.html', {'form': form})


@login_required
def task_update(request, pk):
    """Updates an existing task."""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            
            # Update AI priority suggestion
            priority_data = get_task_priority(task.title, task.description, task.deadline)
            task.ai_priority = priority_data['priority']
            task.ai_score = priority_data['score']
            
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'todos/task_form.html', {'form': form})


@login_required
def task_delete(request, pk):
    """Deletes a task."""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.delete()
    messages.success(request, 'Task deleted successfully.')
    return redirect('task_list')


@login_required
def task_toggle(request, pk):
    """Toggles the completion status of a task."""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.completed = not task.completed
    task.save()
    return redirect('task_list')
