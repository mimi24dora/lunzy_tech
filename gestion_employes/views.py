import json
from django.shortcuts import render, redirect, get_object_or_404
from .decorators import redirect_after_post
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, logout, login as django_login, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib import messages
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.urls import reverse_lazy
from .models import Profile, Pointage, Role
from .forms import (
    UserRegistrationForm, ProfileForm, PointageForm, UserUpdateForm, 
    RoleForm, EmployeForm
)
from django.db import models
from django.conf import settings
import pyotp
import qrcode
from io import BytesIO
import base64


# Vue de connexion personnalisée pour l'application
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('gestion_employes:dashboard')
    form_class = AuthenticationForm
    
    def form_invalid(self, form):
        username = self.request.POST.get('username')
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
            if hasattr(user, 'increment_failed_login_attempts'):
                user.increment_failed_login_attempts()
                remaining_attempts = max(0, 3 - user.failed_login_attempts)
                if remaining_attempts > 0:
                    messages.error(self.request, f"Identifiants invalides. Il vous reste {remaining_attempts} tentative(s).")
                else:
                    messages.error(self.request, "Compte temporairement verrouillé.")
        except User.DoesNotExist:
            messages.error(self.request, "Identifiants invalides.")
        return super().form_invalid(form)

    def form_valid(self, form):
        user = form.get_user()
        
        # Vérifier verrouillage compte
        if hasattr(user, 'is_account_locked') and user.is_account_locked():
            messages.error(self.request, 'Compte temporairement verrouillé.')
            return self.form_invalid(form)
        
        # Vérifier approbation utilisateur
        if not user.is_active:
            if hasattr(user, 'profile') and user.profile.approval_status == 'rejected':
                messages.error(self.request, 'Inscription refusée.')
            else:
                messages.error(self.request, 'Compte en attente d\'approbation.')
            return self.form_invalid(form)
        
        # Stocker l'utilisateur en session pour l'OTP
        self.request.session['pending_user_id'] = user.id
        
        if hasattr(user, 'reset_failed_login_attempts'):
            user.reset_failed_login_attempts()
        
        # Rediriger vers l'OTP au lieu de connecter directement
        return redirect('gestion_employes:login_otp')

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

@login_required
def ajouter_employe(request):
    """Vue pour ajouter un employé depuis l'interface admin"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Sauvegarder l'utilisateur
            user = form.save(commit=False)
            user.is_active = True  # Employé ajouté par admin = directement actif
            user.save()
            
            # Créer le profil avec les champs supplémentaires
            Profile.objects.create(
                user=user,
                telephone=form.cleaned_data['telephone'],
                nom_entreprise=form.cleaned_data['nom_entreprise'],
                statut='actif',
                approval_status='approved'
            )
            
            messages.success(request, f'Employé {user.get_full_name()} ajouté avec succès !')
            return redirect('gestion_employes:liste_employes')
        else:
            messages.error(request, 'Veuillez corriger les erreurs du formulaire.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'gestion_employes/ajouter_employe.html', {
        'form': form,
        'title': 'Ajouter un Employé'
    })

# Vues principales
@login_required
@csrf_protect
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

@login_required
@csrf_protect
def edit_utilisateur(request, pk):
    """Vue pour éditer un utilisateur spécifique"""
    User = get_user_model()
    try:
        user = get_object_or_404(User, pk=pk)
        profile = user.profile if hasattr(user, 'profile') else None
    except:
        messages.error(request, f'Utilisateur avec l\'ID {pk} introuvable.')
        return redirect('gestion_employes:liste_employes')
    
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=profile)
        # Mettre à jour nom et prénom de l'utilisateur
        user.last_name = request.POST.get('last_name', user.last_name)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'Employé mis à jour avec succès !')
            return redirect('gestion_employes:liste_employes')
        else:
            messages.error(request, 'Veuillez corriger les erreurs du formulaire.')
    else:
        profile_form = ProfileForm(instance=profile)
    
    return render(request, 'gestion_employes/utilisateurs/edit_profile.html', {
        'profile_form': profile_form,
        'profile': profile,
        'user': user,
        'is_employe': True
    })

@login_required
def edit_employe(request, pk):
    """Vue pour éditer un employé spécifique"""
    User = get_user_model()
    user = get_object_or_404(User, pk=pk)
    profile = user.profile if hasattr(user, 'profile') else None
    
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=profile)
        # Mettre à jour nom et prénom de l'utilisateur
        user.last_name = request.POST.get('last_name', user.last_name)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.email = request.POST.get('email', request.user.email)
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

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def user_logout(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté.')
    return redirect('gestion_employes:login')

# Vues de gestion des utilisateurs
@login_required
def liste_utilisateurs(request):
    # Vérifier les permissions d'accès
    if (request.user.username not in ['superadmin', 'chakam'] and 
        hasattr(request.user, 'profile') and 
        request.user.profile.role and 
        request.user.profile.role.nom == 'RECEPTIONNISTE'):
        messages.error(request, 'Accès non autorisé à cette section.')
        return redirect('gestion_employes:dashboard')
    
    User = get_user_model()
    
    # Debug: afficher le nom d'utilisateur
    print(f"DEBUG: Utilisateur connecté: {request.user.username}")
    print(f"DEBUG: Est superadmin: {request.user.username == 'superadmin'}")
    
    # Afficher TOUS les utilisateurs (actifs et inactifs) pour voir le problème
    utilisateurs = User.objects.all().prefetch_related('profile', 'profile__role')
    print(f"DEBUG: Nombre total d'utilisateurs: {utilisateurs.count()}")
    print(f"DEBUG: Utilisateurs inactifs: {utilisateurs.filter(is_active=False).count()}")
    
    # Lister tous les utilisateurs pour debug
    for u in utilisateurs:
        print(f"DEBUG: User {u.username} - Active: {u.is_active}")

    
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
    
    # Calculer les statistiques
    total_utilisateurs = utilisateurs.count()
    utilisateurs_actifs = utilisateurs.filter(is_active=True).count()
    utilisateurs_inactifs = utilisateurs.filter(is_active=False).count()
    utilisateurs_conge = utilisateurs.filter(profile__statut='conge').count()
    utilisateurs_sans_role = utilisateurs.filter(profile__role__isnull=True).count()
    
    return render(request, 'gestion_employes/utilisateurs/liste_simple.html', {
        'utilisateurs': utilisateurs,
        'roles': roles,
        'is_superadmin': True,  # Forcer à True pour tester
        'total_utilisateurs': total_utilisateurs,
        'utilisateurs_actifs': utilisateurs_actifs,
        'utilisateurs_inactifs': utilisateurs_inactifs,
        'utilisateurs_conge': utilisateurs_conge,
        'utilisateurs_sans_role': utilisateurs_sans_role
    })

@login_required
def approve_user(request, pk):
    User = get_user_model()
    
    print(f"DEBUG: Tentative d'approbation de l'utilisateur {pk}")
    print(f"DEBUG: Utilisateur connecté: {request.user.username}")
    print(f"DEBUG: Méthode: {request.method}")
    
    user = get_object_or_404(User, pk=pk)
    print(f"DEBUG: Utilisateur trouvé: {user.username}, actif: {user.is_active}")
    
    if request.method == 'POST':
        try:
            # Mettre à jour le statut de l'utilisateur
            user.is_active = True
            user.save()
            print(f"DEBUG: Utilisateur {user.username} activé")
            
            # Vérifier si l'utilisateur a un profil, sinon en créer un
            if not hasattr(user, 'profile'):
                profile = Profile.objects.create(
                    user=user,
                    telephone='',
                    nom_entreprise='',
                    statut='actif',
                    approval_status='approved',
                    poste='Employé'
                )
                print(f"DEBUG: Profil créé pour {user.username} avec matricule {profile.matricule}")
            else:
                profile = user.profile
                profile.statut = 'actif'
                profile.approval_status = 'approved'
                if not profile.matricule:
                    profile.matricule = None
                if not profile.poste:
                    profile.poste = 'Employé'
                profile.save()
                print(f"DEBUG: Profil mis à jour pour {user.username} avec matricule {profile.matricule}")
            
            messages.success(request, f'Le compte de {user.username} a été approuvé avec succès.')
            
        except Exception as e:
            print(f"DEBUG: Erreur lors de l'approbation: {str(e)}")
            messages.error(request, f'Une erreur est survenue lors de l\'approbation du compte: {str(e)}')
    
    return redirect('gestion_employes:liste_utilisateurs')

@login_required
def reject_user(request, pk):
    User = get_user_model()
    
    # Supprimer la vérification des droits pour permettre au superadmin de refuser
    
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
@login_required
def dashboard(request):
    User = get_user_model()
    
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

def gestion_permissions(request, pk):
    """Vue pour gérer les permissions d'un rôle"""
    role = get_object_or_404(Role, pk=pk)
    
    if request.method == 'POST':
        permissions = {
            'users': {
                'view': 'view_users' in request.POST,
                'edit': 'edit_users' in request.POST,
                'delete': 'delete_users' in request.POST,
                'manage': 'manage_users' in request.POST
            },
            'roles': {
                'view': 'view_roles' in request.POST,
                'edit': 'edit_roles' in request.POST,
                'delete': 'delete_roles' in request.POST,
                'manage_permissions': 'manage_permissions' in request.POST
            }
        }
        role.permissions = permissions
        role.save()
        messages.success(request, f'Permissions du rôle {role.get_nom_display()} mises à jour avec succès')
        return redirect('gestion_employes:liste_roles')
    
    return render(request, 'gestion_employes/roles/permissions.html', {'role': role})

def supprimer_role(request, pk):
    role = get_object_or_404(Role, pk=pk)
    
    if request.method == 'POST':
        role.delete()
        messages.success(request, f'Rôle {role.get_nom_display()} supprimé avec succès')
        return redirect('gestion_employes:liste_roles')
    
    return render(request, 'gestion_employes/roles/confirm_delete.html', {'role': role})

# Autres vues (employés, pointage, etc.) restent inchangées
def liste_employes(request):
    tab = request.GET.get('tab', 'employes')
    
    if tab == 'presences':
        # Pour l'onglet présences, afficher seulement les utilisateurs actifs
        profiles = Profile.objects.select_related('user', 'role').filter(user__is_active=True, statut='actif')
    else:
        # Pour l'onglet employés, afficher tous les profils
        profiles = Profile.objects.select_related('user', 'role').all()
    
    return render(request, 'gestion_employes/liste_employes.html', {
        'profiles': profiles,
        'current_tab': tab
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

# Vues de réinitialisation de mot de passe
class CustomPasswordResetView(PasswordResetView):
    template_name = 'gestion_employes/password_reset.html'
    email_template_name = 'gestion_employes/password_reset_email.html'
    success_url = reverse_lazy('gestion_employes:password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'gestion_employes/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'gestion_employes/password_reset_confirm.html'
    success_url = reverse_lazy('gestion_employes:password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'gestion_employes/password_reset_complete.html'

# Vues fonctions pour compatibilité
password_reset_request = CustomPasswordResetView.as_view()
password_reset_done = CustomPasswordResetDoneView.as_view()
password_reset_confirm = CustomPasswordResetConfirmView.as_view()
password_reset_complete = CustomPasswordResetCompleteView.as_view()

# Vues 2FA
@login_required
def setup_2fa(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        secret = request.session.get('2fa_secret')
        
        if secret and pyotp.TOTP(secret).verify(token):
            profile = request.user.profile
            profile.two_factor_secret = secret
            profile.two_factor_enabled = True
            profile.save()
            del request.session['2fa_secret']
            messages.success(request, '2FA activé avec succès !')
            return redirect('gestion_employes:dashboard')
        else:
            messages.error(request, 'Code invalide. Veuillez réessayer.')
    
    # Générer secret et QR code
    secret = pyotp.random_base32()
    request.session['2fa_secret'] = secret
    
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=request.user.email,
        issuer_name="Lunzy Tech"
    )
    
    # Générer QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_code_img = base64.b64encode(buffer.getvalue()).decode()
    
    return render(request, 'gestion_employes/2fa_setup.html', {
        'secret': secret,
        'qr_code': qr_code_img
    })

@login_required
def verify_2fa(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        profile = request.user.profile
        
        if profile.two_factor_secret and pyotp.TOTP(profile.two_factor_secret).verify(token):
            request.session['2fa_verified'] = True
            messages.success(request, 'Authentification 2FA réussie !')
            return redirect('gestion_employes:dashboard')
        else:
            messages.error(request, 'Code 2FA invalide.')
    
    return render(request, 'gestion_employes/2fa_verify.html')

@login_required
def disable_2fa(request):
    if request.method == 'POST':
        profile = request.user.profile
        profile.two_factor_enabled = False
        profile.two_factor_secret = ''
        profile.save()
        messages.success(request, '2FA désactivé avec succès !')
        return redirect('gestion_employes:dashboard')
    
    return render(request, 'gestion_employes/2fa_disable.html')

def login_otp(request):
    """Vue pour l'authentification OTP obligatoire"""
    print(f"DEBUG: Accès à login_otp")
    print(f"DEBUG: Session keys: {list(request.session.keys())}")
    
    if 'pending_user_id' not in request.session:
        print(f"DEBUG: Pas de pending_user_id en session")
        messages.error(request, 'Session expirée. Veuillez vous reconnecter.')
        return redirect('gestion_employes:login')
    
    User = get_user_model()
    try:
        user = User.objects.get(id=request.session['pending_user_id'])
        profile = user.profile
    except (User.DoesNotExist, AttributeError):
        messages.error(request, 'Erreur de session. Veuillez vous reconnecter.')
        return redirect('gestion_employes:login')
    
    # Générer le secret OTP si nécessaire
    if not profile.two_factor_secret:
        profile.two_factor_secret = pyotp.random_base32()
        profile.save()
    
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code', '').strip()
        
        if otp_code and profile.verify_2fa_token(otp_code):
            # Connexion réussie
            django_login(request, user)
            request.session.pop('pending_user_id', None)
            messages.success(request, 'Connexion réussie !')
            return redirect('gestion_employes:dashboard')
        else:
            messages.error(request, 'Code OTP invalide. Vérifiez votre application d\'authentification.')
    
    # Générer le QR code (taille réduite)
    totp_uri = pyotp.totp.TOTP(profile.two_factor_secret).provisioning_uri(
        name=user.email or user.username,
        issuer_name="Lunzy Tech"
    )
    
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(totp_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_code = base64.b64encode(buffer.getvalue()).decode()
    
    return render(request, 'gestion_employes/login_otp.html', {
        'show_qr': True,
        'qr_code': qr_code,
        'secret': profile.two_factor_secret,
        'user_email': user.email or user.username
    })