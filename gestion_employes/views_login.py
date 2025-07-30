from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.utils import timezone

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Vérifier si l'utilisateur existe
        try:
            user_obj = User.objects.get(username=username)
            
            # Vérifier si le compte est verrouillé
            if user_obj.is_account_locked():
                messages.error(request, 'Votre compte est temporairement verrouillé après 3 tentatives échouées. Veuillez réessayer dans 30 minutes.')
                return render(request, 'accounts/login.html', {'form': AuthenticationForm()})
            
            # Vérifier si le compte est actif
            if not user_obj.is_active:
                messages.error(request, 'Votre compte est en attente d\'approbation par un administrateur.')
                return render(request, 'accounts/login.html', {'form': AuthenticationForm()})
                
        except User.DoesNotExist:
            user_obj = None
        
        # Authentifier l'utilisateur
        user = authenticate(request, username=username, password=password)
        if user is not None:
            user.reset_failed_login_attempts()
            login(request, user)
            messages.success(request, f'Connexion réussie! Bienvenue {user.get_full_name() or user.username}.')
            return redirect('gestion_employes:dashboard')
        else:
            # Incrémenter les tentatives échouées si l'utilisateur existe
            if user_obj:
                user_obj.increment_failed_login_attempts()
                remaining = max(0, 3 - user_obj.failed_login_attempts)
                if remaining > 0:
                    messages.error(request, f'Nom d\'utilisateur ou mot de passe incorrect. Il vous reste {remaining} tentative(s).')
                else:
                    messages.error(request, 'Votre compte est temporairement verrouillé après 3 tentatives échouées. Veuillez réessayer dans 30 minutes.')
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})