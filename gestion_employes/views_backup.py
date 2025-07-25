import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, logout, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from .models import Profile, Pointage, Role
from .forms import UserRegistrationForm, ProfileForm, PointageForm, UserUpdateForm, RoleForm, EmployeForm

User = get_user_model()

# Vues d'authentification
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.')
            return redirect('gestion_employes:login')
        else:
            messages.error(request, 'Veuillez corriger les erreurs du formulaire.')
    else:
        form = UserRegistrationForm()
    return render(request, 'gestion_employes/register.html', {
        'form': form,
        'title': 'Inscription'
    })

# Vues principales
@login_required
def edit_profile(request):
    profile = request.user.profile if hasattr(request.user, 'profile') else None
    
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=profile)
        # Mettre à jour nom et prénom de l'utilisateur
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.email = request.POST.get('email', request.user.email)
        request.user.save()
        
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Profil mis à jour avec succès !')
            return redirect('gestion_employes:dashboard')
        else:
            messages.error(request, 'Veuillez corriger les erreurs du formulaire.')
    else:
        profile_form = ProfileForm(instance=profile)
    
    return render(request, 'gestion_employes/utilisateurs/edit_profile.html', {
        'profile_form': profile_form,
        'profile': profile,
        'user': request.user
    })

@require_http_methods(['GET'])
def user_logout(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté.')
    return redirect('gestion_employes:login')

# Vues de gestion des utilisateurs
def liste_utilisateurs(request):
    utilisateurs = User.objects.all().prefetch_related('profile', 'profile__role')
    roles = Role.objects.all()
    return render(request, 'gestion_employes/utilisateurs/liste.html', {
        'utilisateurs': utilisateurs,
        'roles': roles
    })

@login_required
def approve_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.is_active = True
        user.save()
        messages.success(request, f'Le compte de {user.username} a été activé avec succès.')
        return redirect('gestion_employes:liste_utilisateurs')
    
    return redirect('gestion_employes:liste_utilisateurs')

@login_required
def reject_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        user.delete()
        messages.success(request, f'Le compte de {user.username} a été refusé et supprimé.')
        return redirect('gestion_employes:liste_utilisateurs')
    
    return redirect('gestion_employes:liste_utilisateurs')

def liste_employes(request):
    profiles = Profile.objects.all().select_related('user')
    return render(request, 'gestion_employes/liste_employes.html', {
        'profiles': profiles
    })

def modifier_profile(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    user = profile.user
    
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=profile)
        # Mettre à jour nom et prénom de l'utilisateur
        user.last_name = request.POST.get('last_name', user.last_name)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.save()
        if profile_form.is_valid():
            profile = profile_form.save()
            messages.success(request, 'Profil mis à jour avec succès !')
            return redirect('gestion_employes:liste_employes')
        else:
            messages.error(request, 'Veuillez corriger les erreurs du formulaire.')
    else:
        profile_form = ProfileForm(instance=profile)
    
    return render(request, 'gestion_employes/utilisateurs/edit_profile.html', {
        'profile_form': profile_form,
        'profile': profile,
        'user': user
    })

def supprimer_profile(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    
    if request.method == 'POST':
        profile.delete()
        messages.success(request, 'Profil supprimé avec succès !')
        return redirect('gestion_employes:liste_employes')
    
    return render(request, 'gestion_employes/utilisateurs/delete_profile.html', {
        'profile': profile
    })

def update_utilisateur(request, pk):
    user = get_object_or_404(User, pk=pk)
    roles = Role.objects.all()
    
    # Vérifier si le profil existe déjà
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = None
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)
        role_id = request.POST.get('role')
        
        if user_form.is_valid() and profile_form.is_valid():
            try:
                # Sauvegarder l'utilisateur
                user = user_form.save()
                
                # Sauvegarder le profil
                if profile:
                    profile = profile_form.save()
                else:
                    profile = profile_form.save(commit=False)
                    profile.user = user
                    profile.save()
                
                # Mettre à jour le rôle
                if role_id:
                    role = get_object_or_404(Role, id=role_id)
                    if hasattr(user, 'profile'):
                        user.profile.role = role
                        user.profile.save()
                
                messages.success(request, 'Utilisateur et profil mis à jour avec succès !')
                return redirect('gestion_employes:liste_utilisateurs')
            except Exception as e:
                print("Erreur lors de la sauvegarde:", str(e))
                messages.error(request, f'Erreur lors de la sauvegarde: {str(e)}')
                return render(request, 'gestion_employes/utilisateurs/edit.html', {
                    'user_form': user_form,
                    'profile_form': profile_form,
                    'utilisateur': user,
                    'roles': roles
                })
        else:
            # Afficher les erreurs spécifiques
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f'Erreur dans {field}: {error}')
            for field, errors in profile_form.errors.items():
                for error in errors:
                    messages.error(request, f'Erreur dans {field}: {error}')
            
            # Rediriger vers la page de modification avec les erreurs
            return render(request, 'gestion_employes/utilisateurs/edit.html', {
                'user_form': user_form,
                'profile_form': profile_form,
                'utilisateur': user,
                'roles': roles
            })
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileForm(instance=profile)
        
    return render(request, 'gestion_employes/utilisateurs/edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'utilisateur': user,
        'roles': roles
    })

def delete_utilisateur(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Utilisateur supprimé avec succès !')
        return redirect('gestion_employes:liste_utilisateurs')
    
    return render(request, 'gestion_employes/utilisateurs/delete.html', {
        'user': user
    })

def voir_utilisateur(request, pk):
    utilisateur = get_object_or_404(User, pk=pk)
    profile = utilisateur.profile if hasattr(utilisateur, 'profile') else None
    pointages = Pointage.objects.filter(profile=profile).order_by('-date') if profile else None
    
    context = {
        'utilisateur': utilisateur,
        'profile': profile,
        'pointages': pointages,
        'est_super_admin': request.user.is_superuser
    }

    return render(request, 'gestion_employes/utilisateurs/view.html', context)

def view_user(request):
    utilisateurs = User.objects.all()
    return render(request, 'gestion_employes/utilisateurs/view_user.html', {
        'utilisateurs': utilisateurs
    })

def modifier_utilisateur(request, pk):
    user = get_object_or_404(User, pk=pk)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = None
    
    roles = Role.objects.all()
    
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)
        role_id = request.POST.get('role')
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            
            # Sauvegarder ou créer le profil
            if profile:
                profile = profile_form.save()
            else:
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()
            
            # Mettre à jour le rôle de l'utilisateur
            if role_id:
                role = get_object_or_404(Role, id=role_id)
                user.role = role
                user.save()            
            messages.success(request, 'Utilisateur et profil mis à jour avec succès !')
            return redirect('gestion_employes:liste_utilisateurs')
        else:
            messages.error(request, 'Veuillez corriger les erreurs du formulaire.')
            return render(request, 'gestion_employes/utilisateurs/edit.html', {
                'user_form': user_form,
                'profile_form': profile_form,
                'user': user,
                'roles': roles
            })
    else:
        user_form = UserRegistrationForm(instance=user)
        profile_form = ProfileForm(instance=profile)
        
    return render(request, 'gestion_employes/utilisateurs/edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'user': user,
        'roles': roles
    })

def changer_role(request, pk):
    """Vue pour changer le rôle d'un utilisateur via AJAX"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            user = get_object_or_404(User, pk=pk)
            role_id = request.POST.get('role_id')
            
            if role_id:
                role = get_object_or_404(Role, id=role_id)
                user.role = role
                user.save()
                
                return JsonResponse({
                    'success': True,
                    'role': {
                        'nom': role.nom
                    }
                })
            
            return JsonResponse({'success': False, 'error': 'Aucun rôle sélectionné'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

def modifier_utilisateur(request, pk):
    user = get_object_or_404(User, pk=pk)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = None
    
    roles = Role.objects.all()
    
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)
        role_id = request.POST.get('role')
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            
            # Sauvegarder ou créer le profil
            if profile:
                profile = profile_form.save()
            else:
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()
            
            # Mettre à jour le rôle de l'utilisateur
            if role_id:
                role = get_object_or_404(Role, id=role_id)
                user.role = role
                user.save()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Utilisateur et profil mis à jour avec succès !',
                    'user': {
                        'id': user.id,
                        'get_full_name': user.get_full_name(),
                        'username': user.username,
                        'email': user.email,
                        'profile': {
                            'matricule': profile.matricule if profile else '',
                            'telephone': profile.telephone if profile else '',
                            'poste': profile.poste if profile else '',
                            'statut': profile.statut if profile else '',
                            'get_statut_display': profile.get_statut_display() if profile else '',
                            'get_statut_badge': profile.get_statut_badge() if profile else 'secondary'
                        },
                        'role': {
                            'nom': user.role.nom if user.role else None
                        } if user.role else None
                    }
                })
            else:
                messages.success(request, 'Utilisateur et profil mis à jour avec succès !')
                return redirect('gestion_employes:liste_utilisateurs')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': {
                        'user': dict(user_form.errors),
                        'profile': dict(profile_form.errors)
                    }
                })
            
            messages.error(request, 'Veuillez corriger les erreurs du formulaire.')
            return render(request, 'gestion_employes/utilisateurs/form_modifier.html', {
                'user_form': user_form,
                'profile_form': profile_form,
                'user': user,
                'roles': roles
            })
    else:
        user_form = UserRegistrationForm(instance=user)
        profile_form = ProfileForm(instance=profile) if profile else ProfileForm(initial={'user': user})
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return render(request, 'gestion_employes/utilisateurs/form_modifier.html', {
                'user_form': user_form,
                'profile_form': profile_form,
                'user': user,
                'roles': roles
            })
        else:
            return render(request, 'gestion_employes/utilisateurs/form_modifier.html', {
                'user_form': user_form,
                'profile_form': profile_form,
                'user': user,
                'roles': roles
            })

def supprimer_utilisateur(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Utilisateur supprimé avec succès !')
        return redirect('gestion_employes:view_user')
    
    return render(request, 'gestion_employes/utilisateurs/supprimer.html', {
        'user': user
    })

def ajouter_utilisateur(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        employe_form = EmployeForm(request.POST)
        
        if user_form.is_valid() and employe_form.is_valid():
            user = user_form.save()
            employe = employe_form.save(commit=False)
            employe.user = user
            employe.save()
            
            messages.success(request, 'Utilisateur et employé créés avec succès !')
            return redirect('gestion_employes:view_user')
        else:
            messages.error(request, 'Veuillez corriger les erreurs du formulaire.')
    else:
        user_form = UserRegistrationForm()
        employe_form = EmployeForm()
    
    return render(request, 'gestion_employes/utilisateurs/ajouter.html', {
        'user_form': user_form,
        'employe_form': employe_form
    })

# Vues principales
def dashboard(request):
    # Statistiques
    total_profiles = Profile.objects.count()
    profiles_actifs = Profile.objects.filter(statut='actif').count()
    profiles_inactifs = Profile.objects.filter(statut='inactif').count()
    profiles_conges = Profile.objects.filter(statut='conge').count()
    pointages_jour = Pointage.objects.filter(date=timezone.now().date()).count()
    profiles = Profile.objects.all()
    derniers_pointages = Pointage.objects.order_by('-date')[:5]
    roles = Role.objects.all()
    nombre_roles = roles.count()
    
    context = {
        'total_profiles': total_profiles,
        'profiles_actifs': profiles_actifs,
        'profiles_inactifs': profiles_inactifs,
        'profiles_conges': profiles_conges,
        'pointages_jour': pointages_jour,
        'profiles': profiles,
        'derniers_pointages': derniers_pointages,
        'roles': roles,
        'nombre_roles': nombre_roles,
        'utilisateurs': User.objects.all().prefetch_related('profile')
    }
    return render(request, 'gestion_employes/dashboard.html', context)

def liste_roles(request):
    roles = Role.objects.all()
    return render(request, 'gestion_employes/roles/liste_roles.html', {'roles': roles})

def ajouter_role(request):
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save()
            messages.success(request, f'Rôle {role.get_nom_display()} créé avec succès')
            return redirect('gestion_employes:liste_roles')
    else:
        form = RoleForm()
    return render(request, 'gestion_employes/roles/form_role.html', {
        'form': form,
        'title': 'Ajouter un rôle'
    })

def modifier_role(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            role = form.save()
            messages.success(request, f'Rôle {role.get_nom_display()} mis à jour avec succès')
            return redirect('gestion_employes:liste_roles')
    else:
        form = RoleForm(instance=role)
    return render(request, 'gestion_employes/roles/form_role.html', {
        'form': form,
        'title': f'Modifier le rôle {role.get_nom_display()}'
    })

def supprimer_role(request, pk):
    role = get_object_or_404(Role, pk=pk)
    
    if request.method == 'POST':
        role.delete()
        messages.success(request, f'Rôle {role.get_nom_display()} supprimé avec succès')
        return redirect('gestion_employes:liste_roles')
    
    return render(request, 'gestion_employes/roles/confirm_delete.html', {'role': role})

def gestion_permissions(request, pk):
    role = get_object_or_404(Role, pk=pk)
    modules = ['employes', 'pointage', 'utilisateurs', 'roles']
    permissions = {
        'employes': ['lister', 'ajouter', 'modifier', 'supprimer', 'consulter'],
        'pointage': ['pointage', 'historique', 'consulter'],
        'utilisateurs': ['lister', 'ajouter', 'modifier', 'supprimer', 'consulter'],
        'roles': ['lister', 'ajouter', 'modifier', 'supprimer', 'consulter']
    }
    
    if request.method == 'POST':
        permissions_data = {}
        for module in modules:
            permissions_data[module] = []
            for perm in permissions[module]:
                if request.POST.get(f'{module}_{perm}') == 'on':
                    permissions_data[module].append(perm)
        
        # Convertir en JSON et sauvegarder
        role.permissions = json.dumps(permissions_data)
        role.save()
        messages.success(request, f'Permissions du rôle {role.get_nom_display()} mises à jour avec succès')
        return redirect('gestion_employes:liste_roles')
    
    # Charger les permissions existantes
    try:
        current_permissions = json.loads(role.permissions)
    except (json.JSONDecodeError, TypeError):
        current_permissions = {}
    
    return render(request, 'gestion_employes/roles/gestion_permissions.html', {
        'role': role,
        'modules': modules,
        'permissions': permissions,
        'current_permissions': current_permissions
    })

def liste_employes(request):
    profiles = Profile.objects.all()
    return render(request, 'gestion_employes/liste_employes.html', {'profiles': profiles})

def ajouter_employe(request):
    User = get_user_model()
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        employe_form = EmployeForm(request.POST)
        
        if user_form.is_valid() and employe_form.is_valid():
            user = user_form.save()
            employe = employe_form.save(commit=False)
            employe.user = user
            employe.save()
            
            messages.success(request, 'Utilisateur et employé créés avec succès !')
            return redirect('gestion_employes:liste_employes')
    else:
        user_form = UserCreationForm()
        employe_form = EmployeForm()
    
    return render(request, 'gestion_employes/ajouter_employe.html', {
        'user_form': user_form,
        'employe_form': employe_form
    })

def pointage(request):
    if request.method == 'POST':
        form = PointageForm(request.POST)
        if form.is_valid():
            pointage = form.save(commit=False)
            pointage.date = timezone.now().date()
            pointage.heure = timezone.now().time()
            pointage.save()
            messages.success(request, 'Pointage enregistré avec succès !')
            return redirect('dashboard')
    else:
        form = PointageForm()
    return render(request, 'gestion_employes/pointage.html', {'form': form})

def historique_pointages(request):
    pointages = Pointage.objects.all().order_by('-date')
    return render(request, 'gestion_employes/historique_pointages.html', {'pointages': pointages})
