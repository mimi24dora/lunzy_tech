from .permissions import has_permission

def user_permissions(request):
    """
    Ajoute les informations de rôle et de permission à tous les templates.
    """
    if not request.user.is_authenticated:
        return {}
    
    # Vérifier si l'utilisateur a un profil et un rôle
    has_profile = hasattr(request.user, 'profile')
    user_role = request.user.profile.role if has_profile and hasattr(request.user.profile, 'role') else None
    
    return {
        'user_role': user_role.nom if user_role else None,
        'is_superadmin': request.user.username == 'superadmin',
        'has_permission': lambda perm: has_permission(request.user, perm) if request.user.is_authenticated else False
    }
