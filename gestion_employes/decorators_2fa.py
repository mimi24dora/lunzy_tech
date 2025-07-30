from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden

def role_required(allowed_roles):
    """Décorateur pour vérifier les rôles"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if request.user.role not in allowed_roles:
                messages.error(request, 'Accès non autorisé')
                return HttpResponseForbidden('Accès refusé')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def permission_required(permission):
    """Décorateur pour vérifier les permissions"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if not request.user.has_permission(permission):
                messages.error(request, 'Permission insuffisante')
                return HttpResponseForbidden('Permission refusée')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def admin_required(view_func):
    """Décorateur pour les admins uniquement"""
    return role_required(['admin'])(view_func)

def editor_or_admin_required(view_func):
    """Décorateur pour éditeurs et admins"""
    return role_required(['admin', 'editor'])(view_func)