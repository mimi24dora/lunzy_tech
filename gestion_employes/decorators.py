from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Profile

def role_required(*roles):
    """
    Décorateur pour vérifier que l'utilisateur a un des rôles spécifiés.
    Utilisation : @role_required('admin', 'manager')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Veuillez vous connecter pour accéder à cette page.')
                return redirect('login')
            
            # Le superadmin a accès à tout
            if request.user.username == 'superadmin':
                return view_func(request, *args, **kwargs)
            
            # Vérifier si l'utilisateur a un profil et un rôle
            if not hasattr(request.user, 'profile') or not request.user.profile.role:
                messages.error(request, 'Vous n\'avez pas les permissions nécessaires pour accéder à cette page.')
                return redirect('gestion_employes:dashboard')
            
            # Vérifier si le rôle de l'utilisateur est autorisé
            user_role = request.user.profile.role.nom
            if user_role not in roles:
                messages.error(request, 'Accès refusé. Vous n\'avez pas les droits nécessaires.')
                return redirect('gestion_employes:dashboard')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def permission_required(permission):
    """
    Décorateur pour vérifier que l'utilisateur a une permission spécifique.
    Utilisation : @permission_required('gestion_employes.view_profile')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Veuillez vous connecter pour accéder à cette page.')
                return redirect('login')
            
            # Le superadmin a toutes les permissions
            if request.user.username == 'superadmin':
                return view_func(request, *args, **kwargs)
            
            # Vérifier si l'utilisateur a un profil et un rôle
            if not hasattr(request.user, 'profile') or not request.user.profile.role:
                messages.error(request, 'Vous n\'avez pas les permissions nécessaires pour accéder à cette page.')
                return redirect('gestion_employes:dashboard')
            
            # Vérifier la permission
            role = request.user.profile.role
            app_label, codename = permission.split('.')
            
            if not role.permissions or app_label not in role.permissions or codename not in role.permissions[app_label]:
                messages.error(request, 'Accès refusé. Vous n\'avez pas les droits nécessaires.')
                return redirect('gestion_employes:dashboard')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def redirect_after_post(get_redirect_url):
    """
    Décorateur pour rediriger vers une URL spécifiée après une requête POST réussie.
    Si un paramètre 'next' est présent dans la requête GET, il sera utilisé pour la redirection.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.method == 'POST':
                response = view_func(request, *args, **kwargs)
                if hasattr(response, 'url'):  # Si c'est une redirection
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                return response
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
