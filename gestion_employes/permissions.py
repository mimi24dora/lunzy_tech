from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles):
    """
    Décorateur pour vérifier que l'utilisateur a un rôle autorisé.
    Utilisation : @role_required(['admin', 'manager'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Vérifier si l'utilisateur est authentifié
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
            if user_role not in allowed_roles:
                messages.error(request, 'Accès refusé. Vous n\'avez pas les droits nécessaires.')
                return redirect('gestion_employes:dashboard')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def has_permission(user, permission):
    """
    Vérifie si un utilisateur a une permission spécifique.
    Utilisation : has_permission(request.user, 'gestion_employes.view_profile')
    """
    # Le superadmin a toutes les permissions
    if user.username == 'superadmin':
        return True
    
    # Vérifier si l'utilisateur a un profil et un rôle
    if not hasattr(user, 'profile') or not user.profile.role:
        return False
    
    # Vérifier les permissions dans le rôle
    role = user.profile.role
    if not role.permissions:
        return False
    
    # Vérifier si la permission est dans les permissions du rôle
    app_label, codename = permission.split('.')
    return app_label in role.permissions and codename in role.permissions[app_label]
