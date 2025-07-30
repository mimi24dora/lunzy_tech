import json
from django.shortcuts import render, redirect, get_object_or_404
from .decorators import redirect_after_post
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, logout, login as django_login, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from .models import Profile, Pointage, Role
from .forms import (
    UserRegistrationForm, ProfileForm, PointageForm, UserUpdateForm, 
    RoleForm, EmployeForm, TwoFactorSetupForm, TwoFactorVerifyForm
)

User = get_user_model()

# Vues 2FA
@login_required
def setup_2fa(request):
    """Vue pour configurer le 2FA"""
    if request.user.is_2fa_enabled:
        messages.info(request, 'Le 2FA est déjà activé sur votre compte.')
        return redirect('gestion_employes:dashboard')
    
    # Générer la clé secrète si elle n'existe pas
    request.user.generate_2fa_secret()
    
    if request.method == 'POST':
        form = TwoFactorSetupForm(request.user, request.POST)
        if form.is_valid():
            # Activer le 2FA et générer les codes de récupération
            request.user.is_2fa_enabled = True
            request.user.save()
            backup_codes = request.user.generate_backup_codes()
            
            messages.success(request, 'Le 2FA a été activé avec succès!')
            return render(request, 'gestion_employes/2fa/backup_codes.html', {
                'backup_codes': backup_codes
            })
    else:
        form = TwoFactorSetupForm(request.user)
    
    # Générer le QR code
    qr_code = request.user.generate_qr_code()
    secret_key = request.user.two_factor_secret
    
    return render(request, 'gestion_employes/2fa/setup.html', {
        'form': form,
        'qr_code': qr_code,
        'secret_key': secret_key
    })

@login_required
def disable_2fa(request):
    """Vue pour désactiver le 2FA"""
    if request.method == 'POST':
        request.user.is_2fa_enabled = False
        request.user.two_factor_secret = ''
        request.user.backup_codes = []
        request.user.save()
        
        messages.success(request, 'Le 2FA a été désactivé.')
        return redirect('gestion_employes:dashboard')
    
    return render(request, 'gestion_employes/2fa/disable.html')

def verify_2fa(request):
    """Vue pour vérifier le code 2FA lors de la connexion"""
    # Vérifier si l'utilisateur est en cours d'authentification 2FA
    user_id = request.session.get('pre_2fa_user_id')
    if not user_id:
        messages.error(request, 'Session expirée. Veuillez vous reconnecter.')
        return redirect('gestion_employes:login')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Utilisateur non trouvé.')
        return redirect('gestion_employes:login')
    
    if request.method == 'POST':
        form = TwoFactorVerifyForm(user, request.POST)
        if form.is_valid():
            # Authentifier l'utilisateur
            django_login(request, user)
            
            # Nettoyer la session
            if 'pre_2fa_user_id' in request.session:
                del request.session['pre_2fa_user_id']
            
            # Réinitialiser les tentatives de connexion échouées
            user.reset_failed_login_attempts()
            
            messages.success(request, f'Connexion réussie! Bienvenue {user.get_full_name()}.')
            return redirect('gestion_employes:dashboard')
        else:
            user.increment_failed_login_attempts()
            remaining_attempts = max(0, 5 - user.failed_login_attempts)
            if remaining_attempts > 0:
                messages.error(request, f'Code invalide. Il vous reste {remaining_attempts} tentative(s).')
            else:
                messages.error(request, 'Compte temporairement verrouillé pour 30 minutes.')
                return redirect('gestion_employes:login')
    else:
        form = TwoFactorVerifyForm(user)
    
    return render(request, 'gestion_employes/2fa/verify.html', {
        'form': form,
        'user': user
    })

# Vue de connexion modifiée
class CustomLoginView(LoginView):
    template_name = 'gestion_employes/login.html'
    success_url = reverse_lazy('gestion_employes:dashboard')

    def form_valid(self, form):
        user = form.get_user()
        
        # Vérifier si le compte est verrouillé
        if user.is_account_locked():
            messages.error(
                self.request,
                'Votre compte est temporairement verrouillé en raison de trop nombreuses tentatives de connexion. '
                'Veuillez réessayer dans 30 minutes.'
            )
            return self.form_invalid(form)
        
        # Super admin credentials
        SUPER_ADMIN_USERNAME = 'superadmin'
        SUPER_ADMIN_PASSWORD = 'SuperAdmin2025!'
        SUPER_ADMIN_EMAIL = 'superadmin@lunzytech.com'
        
        # Check if this is the super admin
        if (user.username == SUPER_ADMIN_USERNAME and 
            user.email == SUPER_ADMIN_EMAIL):
            # Super admin peut accéder directement ou avec 2FA si activé
            if user.is_2fa_enabled:
                # Stocker l'ID utilisateur pour la vérification 2FA
                self.request.session['pre_2fa_user_id'] = user.id
                return redirect('gestion_employes:verify_2fa')
            else:
                return super().form_valid(form)
        
        # Utilisateur régulier - vérifier l'approbation
        if not user.is_active:
            if hasattr(user, 'profile') and user.profile.approval_status == 'rejected':
                messages.error(self.request, 'Votre demande d\'inscription a été refusée. Veuillez contacter l\'administrateur pour plus d\'informations.')
            else:
                messages.error(
                    self.request,
                    'Votre compte est en attente d\'approbation par un administrateur. '
                    'Vous recevrez un email dès que votre compte sera activé. Merci de votre patience.'
                )
            return self.form_invalid(form)
        
        # Vérifier si le 2FA est activé
        if user.is_2fa_enabled:
            # Stocker l'ID utilisateur pour la vérification 2FA
            self.request.session['pre_2fa_user_id'] = user.id
            return redirect('gestion_employes:verify_2fa')
        
        # Connexion normale sans 2FA
        user.reset_failed_login_attempts()
        return super().form_valid(form)

# Vues d'authentification
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Sauvegarder l'utilisateur
            user = form.save(commit=False)
            user.is_active = False  # L'utilisateur doit être approuvé par un administrateur
            user.save()
            
            # Créer le profil avec les champs supplémentaires
            Profile.objects.create(
                user=user,
                telephone=form.cleaned_data['telephone'],
                nom_entreprise=form.cleaned_data['nom_entreprise'],
                statut='en_attente',
                approval_status='pending'
            )
            
            # Message plus détaillé pour l'utilisateur
            success_message = (
                'Votre compte a été créé avec succès.\n\n'
                'Votre inscription est en cours de traitement par notre équipe. '
                'Vous recevrez un email de confirmation une fois votre compte approuvé.\n\n'
                'Merci de votre compréhension et de votre patience.'
            )
            messages.success(request, success_message)
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
@login_required
def liste_utilisateurs(request):
    # Filtrer les utilisateurs selon le rôle de l'utilisateur connecté
    if request.user.username == 'superadmin':
        utilisateurs = User.objects.all().prefetch_related('profile', 'profile__role')
    else:
        utilisateurs = User.objects.filter(is_active=True).prefetch_related('profile', 'profile__role')
    
    roles = Role.objects.all()
    
    # Vérifier si le super admin existe et lui assigner le rôle approprié
    if request.user.username == 'superadmin':
        try:
            superadmin_role = Role.objects.get(nom='superadmin')
            if not request.user.profile.role:
                request.user.profile.role = superadmin_role
                request.user.profile.save()
        except Role.DoesNotExist:
            # Créer le rôle super admin si nécessaire
            superadmin_role = Role.objects.create(
                nom='superadmin',
                description='Super Administrateur avec tous les droits',
                permissions={
                    'gestion': ['tous'],
                    'utilisateurs': ['tous'],
                    'administration': ['tous']
                }
            )
            request.user.profile.role = superadmin_role
            request.user.profile.save()
    
    return render(request, 'gestion_employes/utilisateurs/liste_amelioree.html', {
        'utilisateurs': utilisateurs,
        'roles': roles,
        'is_superadmin': request.user.username == 'superadmin'
    })

@login_required
def approve_user(request, pk):
    # Seul le super admin peut approuver
    if request.user.username != 'superadmin':
        messages.error(request, 'Vous n\'avez pas les droits nécessaires pour approuver un utilisateur.')
        return redirect('gestion_employes:liste_utilisateurs')
    
    user = get_object_or_404(User, pk=pk)
    
    # Vérifier si l'utilisateur a un profil, sinon en créer un
    if not hasattr(user, 'profile'):
        # Créer un profil par défaut si aucun n'existe
        profile = Profile.objects.create(
            user=user,
            telephone='',
            nom_entreprise='',
            statut='actif',
            approval_status='approved'
        )
    else:
        profile = user.profile
    
    if request.method == 'POST':
        try:
            # Mettre à jour le statut de l'utilisateur
            user.is_active = True
            user.save()
            
            # Mettre à jour le statut du profil
            profile.statut = 'actif'
            profile.approval_status = 'approved'
            profile.save()
            
            messages.success(request, f'Le compte de {user.username} a été approuvé avec succès.')
        except Exception as e:
            messages.error(request, f'Une erreur est survenue lors de l\'approbation du compte: {str(e)}')
        
        return redirect('gestion_employes:liste_utilisateurs')
    
    return redirect('gestion_employes:liste_utilisateurs')

@login_required
def reject_user(request, pk):
    # Seul le super admin peut refuser
    if request.user.username != 'superadmin':
        messages.error(request, 'Vous n\'avez pas les droits nécessaires pour refuser un utilisateur.')
        return redirect('gestion_employes:liste_utilisateurs')
    
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        try:
            # Vérifier si l'utilisateur a un profil, sinon en créer un
            if not hasattr(user, 'profile'):
                # Créer un profil par défaut si aucun n'existe
                profile = Profile.objects.create(
                    user=user,
                    telephone='',
                    nom_entreprise='',
                    statut='inactif',
                    approval_status='rejected'
                )
            else:
                profile = user.profile
                # Mettre à jour le statut du profil
                profile.approval_status = 'rejected'
                profile.statut = 'inactif'
                profile.save()
            
            # Supprimer l'utilisateur
            username = user.username
            user.delete()
            
            messages.success(request, f'Le compte de {username} a été refusé et supprimé avec succès.')
        except Exception as e:
            messages.error(request, f'Une erreur est survenue lors du refus du compte: {str(e)}')
        
        return redirect('gestion_employes:liste_utilisateurs')
    
    return redirect('gestion_employes:liste_utilisateurs')

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

# Vues pour les rôles (inchangées)
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

# Autres vues (employés, pointage, etc.) restent inchangées
def liste_employes(request):
    profiles = Profile.objects.select_related('user', 'role').all()
    return render(request, 'gestion_employes/liste_employes.html', {'profiles': profiles})

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