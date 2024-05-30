from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import UserRegisterForm, CustomAuthenticationForm
from .models import Task
from .forms import TaskForm

##### Showw list of tasks #############
@login_required
def task_list(request):
    status_filter = request.GET.get('status')
    sort_by = request.GET.get('sort_by', 'due_date')

    assigned_tasks = Task.objects.filter(assigned_user=request.user)
    created_tasks = Task.objects.filter(created_by=request.user)

    if status_filter == 'incomplete':
        assigned_tasks = assigned_tasks.filter(status='IN')
        created_tasks = created_tasks.filter(status='IN')
    elif status_filter == 'complete':
        assigned_tasks = assigned_tasks.filter(status='CO')
        created_tasks = created_tasks.filter(status='CO')

    if sort_by == 'priority':
        assigned_tasks = assigned_tasks.order_by('priority')
        created_tasks = created_tasks.order_by('priority')
    else:
        assigned_tasks = assigned_tasks.order_by(sort_by)
        created_tasks = created_tasks.order_by(sort_by)

    return render(request, 'tasks/task_list.html', {
        'assigned_tasks': assigned_tasks,
        'created_tasks': created_tasks,
        'sort_by': sort_by
    })

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'tasks/task_detail.html', {'task': task})

@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.user == task.created_by or request.user == task.assigned_user:
        if request.method == 'POST':
            form = TaskForm(request.POST, instance=task)
            if form.is_valid():
                form.save()
                return redirect('task_detail', pk=task.pk)
        else:
            form = TaskForm(instance=task)
        return render(request, 'tasks/task_form.html', {'form': form})
    else:
        messages.error(request, 'You do not have permission to edit this task.')
        return redirect('task_list')

@login_required
def task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        if request.user == task.assigned_user:
            task.status = 'complete' if 'is_complete' in request.POST else 'incomplete'
            task.save()
        return redirect('task_list')
    return HttpResponseForbidden()

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.user == task.created_by:
        task.delete()
        messages.success(request, 'Task successfully deleted.')
        return redirect('task_list')
    else:
        messages.error(request, 'You do not have permission to delete this task.')
        return redirect('task_list')


##### Registration ######
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f'Your account has been created! You are now logged in as {username}.')
            return redirect('task_list')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = UserRegisterForm()
    return render(request, 'tasks/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'You are now logged in as {username}.')
                return redirect('task_list')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'tasks/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')
