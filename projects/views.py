from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Project
from .forms import ProjectForm


def project_list_view(request):
    projects_list = Project.objects.filter(status='open').order_by('-created_at')
    
    paginator = Paginator(projects_list, 12)
    page_number = request.GET.get('page')
    projects = paginator.get_page(page_number)
    
    context = {'projects': projects}
    return render(request, 'projects/project_list.html', context)


def project_detail_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    context = {
        'project': project,
    }
    return render(request, 'projects/project-details.html', context)


@login_required
def create_project_view(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            messages.success(request, 'Проект успешно создан!')
            return redirect('projects:project_detail', project_id=project.id)
    else:
        form = ProjectForm()
    
    return render(request, 'projects/create-project.html', {
        'form': form,
        'is_edit': False
    })


@login_required
def edit_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if project.owner != request.user:
        messages.error(request, 'Вы не можете редактировать этот проект')
        return redirect('projects:project_detail', project_id=project.id)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Проект успешно обновлен!')
            return redirect('projects:project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'projects/create-project.html', {
        'form': form,
        'is_edit': True
    })


@login_required
@require_POST
def complete_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if project.owner != request.user:
        return JsonResponse({'status': 'error', 'message': 'У вас нет прав'}, status=403)
    
    if project.status != 'open':
        return JsonResponse({'status': 'error', 'message': 'Проект уже завершен'}, status=400)
    
    project.status = 'closed'
    project.save()
    
    return JsonResponse({'status': 'ok', 'project_status': 'closed'})


@login_required
@require_POST
def toggle_participate_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.user in project.participants.all():
        project.participants.remove(request.user)
        is_participant = False
    else:
        project.participants.add(request.user)
        is_participant = True

    count = project.participants.count()
    return JsonResponse(
        {
            "status": "ok",
            "is_participant": is_participant,
            "participant_count": count,
        }
    )


@login_required
@require_POST
def toggle_favorite_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if project in request.user.favorites.all():
        request.user.favorites.remove(project)
        favorited = False
    else:
        request.user.favorites.add(project)
        favorited = True
    
    return JsonResponse({'status': 'ok', 'favorited': favorited})


@login_required
def favorites_view(request):
    favorite_projects = request.user.favorites.all().order_by('-created_at')
    
    paginator = Paginator(favorite_projects, 12)
    page_number = request.GET.get('page')
    projects = paginator.get_page(page_number)
    
    return render(request, 'projects/favorite_projects.html', {'projects': projects})