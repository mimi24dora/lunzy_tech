from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse

@csrf_protect
def custom_login(request):
    """Vue de login personnalisée pour l'application (séparée de l'admin Django)"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Vérifications de sécurité
            if hasattr(user, 'is_account_locked') and user.is_account_locked():
                messages.error(request, 'Compte temporairement verrouillé.')
                return render(request, 'accounts/login.html', {'form': form})
            
            # Vérifier approbation
            if not user.is_active:
                if hasattr(user, 'profile') and user.profile.approval_status == 'rejected':
                    messages.error(request, 'Inscription refusée.')
                else:
                    messages.error(request, 'Compte en attente d\'approbation.')
                return render(request, 'accounts/login.html', {'form': form})
            
            # Créer un profil si nécessaire
            if not hasattr(user, 'profile'):
                from .models import Profile
                Profile.objects.create(user=user)
            
            # Stocker l'utilisateur pour l'OTP
            request.session['pending_user_id'] = user.id
            
            if hasattr(user, 'reset_failed_login_attempts'):
                user.reset_failed_login_attempts()
            
            # Debug
            print(f"DEBUG: Redirection vers OTP pour utilisateur {user.username}")
            print(f"DEBUG: Session pending_user_id = {request.session['pending_user_id']}")
            
            # Rediriger vers l'OTP
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect('/gestion/login/otp/')
        else:
            # Gestion échecs de connexion
            username = request.POST.get('username')
            User = get_user_model()
            try:
                user = User.objects.get(username=username)
                if hasattr(user, 'increment_failed_login_attempts'):
                    user.increment_failed_login_attempts()
                    remaining = max(0, 3 - user.failed_login_attempts)
                    if remaining > 0:
                        messages.error(request, f"Identifiants invalides. {remaining} tentative(s) restante(s).")
                    else:
                        messages.error(request, "Compte verrouillé temporairement.")
            except User.DoesNotExist:
                messages.error(request, "Identifiants invalides.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})