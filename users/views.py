from urllib.parse import quote

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, CustomPasswordChangeForm
from .models import User
from .avatar_generate import build_registration_avatar_png
from projects.models import Project


def register_view(request):
    if request.user.is_authenticated:
        return redirect('projects:project_list')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            avatar_file = build_registration_avatar_png(user.name)
            user.avatar.save("initial.png", avatar_file, save=False)
            user.save()
            
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('projects:project_list')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('projects:project_list')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.name}!')
                return redirect('projects:project_list')
        else:
            messages.error(request, 'Неверный email или пароль')
    else:
        form = UserLoginForm()
    
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('projects:project_list')


def user_detail_view(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    projects = user_obj.owned_projects.all()
    
    context = {
        'user': user_obj,
        'projects': projects,
    }
    return render(request, 'users/user-details.html', context)


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('users:user_detail', user_id=request.user.id)
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменен!')
            return redirect('users:user_detail', user_id=request.user.id)
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'users/change_password.html', {'form': form})


def users_list_view(request):
    users_list = User.objects.all().order_by('id')

    filter_param = request.GET.get('filter')
    skill_param = request.GET.get('skill')

    active_filter = None
    if request.user.is_authenticated and filter_param:
        if filter_param == 'authors_of_favorite_projects':
            favorite_projects = request.user.favorites.all()
            users_list = User.objects.filter(owned_projects__in=favorite_projects).distinct()
            active_filter = 'authors_of_favorite_projects'

        elif filter_param == 'authors_of_my_participated_projects':
            participated_projects = request.user.participated_projects.all()
            users_list = User.objects.filter(owned_projects__in=participated_projects).distinct()
            active_filter = 'authors_of_my_participated_projects'

        elif filter_param == 'users_who_favorite_my_projects':
            my_projects = request.user.owned_projects.all()
            users_list = User.objects.filter(favorites__in=my_projects).distinct()
            active_filter = 'users_who_favorite_my_projects'

        elif filter_param == 'participants_of_my_projects':
            my_projects = request.user.owned_projects.all()
            users_list = User.objects.filter(participated_projects__in=my_projects).distinct()
            active_filter = 'participants_of_my_projects'

    active_skill = skill_param or None
    all_skills = []

    paginator = Paginator(users_list, 12)
    page_number = request.GET.get('page')
    participants = paginator.get_page(page_number)

    query_parts = []
    if filter_param:
        query_parts.append(f"filter={quote(filter_param, safe='')}")
    if skill_param:
        query_parts.append(f"skill={quote(skill_param, safe='')}")
    query_prefix = ("&".join(query_parts) + "&") if query_parts else ""

    context = {
        'participants': participants,
        'page_obj': participants,
        'active_filter': active_filter,
        'active_skill': active_skill,
        'all_skills': all_skills,
        'query_prefix': query_prefix,
    }
    return render(request, 'users/participants.html', context)