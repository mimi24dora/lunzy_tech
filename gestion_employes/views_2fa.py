from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def register_view(request):
    if request.method == 'POST':
        # Créer l'utilisateur
        user = CustomUser.objects.create_user(
            username=request.POST['username'],
            email=request.POST['email'],
            password=request.POST['password'],
            role=request.POST.get('role', 'viewer')
        )
        
        # Générer la clé secrète 2FA
        user.generate_totp_secret()
        
        # Rediriger vers la configuration 2FA
        request.session['user_id'] = user.id
        return redirect('setup_2fa')
    
    return render(request, 'auth/register.html')

def setup_2fa_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('register')
    
    user = CustomUser.objects.get(id=user_id)
    
    if request.method == 'POST':
        token = request.POST.get('token')
        if user.verify_totp(token):
            user.is_2fa_enabled = True
            user.save()
            del request.session['user_id']
            messages.success(request, '2FA configuré avec succès!')
            return redirect('login')
        else:
            messages.error(request, 'Code invalide')
    
    context = {
        'qr_code': user.generate_qr_code(),
        'secret': user.totp_secret
    }
    return render(request, 'auth/setup_2fa.html', context)

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username, password=password)
        
        if user:
            if user.is_2fa_enabled:
                # Stocker l'utilisateur en session pour la 2FA
                request.session['pre_2fa_user_id'] = user.id
                return redirect('verify_2fa')
            else:
                login(request, user)
                return redirect('dashboard')
        else:
            messages.error(request, 'Identifiants invalides')
    
    return render(request, 'auth/login.html')

def verify_2fa_view(request):
    user_id = request.session.get('pre_2fa_user_id')
    if not user_id:
        return redirect('login')
    
    user = CustomUser.objects.get(id=user_id)
    
    if request.method == 'POST':
        token = request.POST.get('token')
        if user.verify_totp(token):
            del request.session['pre_2fa_user_id']
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Code 2FA invalide')
    
    return render(request, 'auth/verify_2fa.html')

@login_required
def dashboard_view(request):
    # Données selon le rôle
    context = {
        'user_role': request.user.role,
        'can_manage_users': request.user.has_permission('manage_users'),
        'sections': get_user_sections(request.user)
    }
    
    return render(request, 'dashboard/index.html', context)

def get_user_sections(user):
    """Retourne les sections accessibles selon le rôle"""
    sections = []
    
    if user.can_access_section('dashboard'):
        sections.append({'name': 'Dashboard', 'url': 'dashboard', 'icon': 'fa-tachometer-alt'})
    
    if user.can_access_section('users'):
        sections.append({'name': 'Utilisateurs', 'url': 'users', 'icon': 'fa-users'})
    
    if user.can_access_section('roles'):
        sections.append({'name': 'Rôles', 'url': 'roles', 'icon': 'fa-user-shield'})
    
    if user.can_access_section('content'):
        sections.append({'name': 'Contenu', 'url': 'content', 'icon': 'fa-edit'})
    
    if user.can_access_section('reports'):
        sections.append({'name': 'Rapports', 'url': 'reports', 'icon': 'fa-chart-bar'})
    
    if user.can_access_section('settings'):
        sections.append({'name': 'Paramètres', 'url': 'settings', 'icon': 'fa-cog'})
    
    return sections