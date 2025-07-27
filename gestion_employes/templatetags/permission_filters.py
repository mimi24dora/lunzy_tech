from django import template
from django.contrib.auth import get_user_model
import json

register = template.Library()
User = get_user_model()

@register.filter
def get_dict_item(dictionary, key):
    """Renvoie la valeur d'un dictionnaire pour une clé donnée"""
    if isinstance(dictionary, dict):
        return dictionary.get(key, [])
    return []

@register.filter
def get_permissions(value, module):
    """Renvoie les permissions pour un module spécifique"""
    try:
        permissions = json.loads(value)
        return permissions.get(module, [])
    except (json.JSONDecodeError, AttributeError, TypeError):
        return []

@register.filter
def has_permission(user, perm):
    """
    Vérifie si l'utilisateur a une permission spécifique.
    
    Args:
        user: L'utilisateur à vérifier (peut être un objet User ou un dictionnaire avec un profil et un rôle)
        perm: La permission à vérifier au format 'app_label.codename'
    """
    # Si l'utilisateur est le superadmin, il a toutes les permissions
    if hasattr(user, 'username') and user.username == 'superadmin':
        return True
    
    # Vérifier si l'utilisateur a un profil et un rôle
    if not hasattr(user, 'profile') or not hasattr(user.profile, 'role'):
        return False
    
    role = user.profile.role
    if not role or not role.permissions:
        return False
    
    # Vérifier si la permission existe dans le rôle de l'utilisateur
    try:
        app_label, codename = perm.split('.')
        return role.permissions.get(app_label, {}).get(codename, False)
    except (ValueError, AttributeError):
        return False

@register.filter
def has_any_permission(user, perms):
    """
    Vérifie si l'utilisateur a au moins une des permissions spécifiées.
    
    Args:
        user: L'utilisateur à vérifier
        perms: Chaîne de permissions séparées par des virgules
    """
    if not user or not perms:
        return False
        
    permission_list = [p.strip() for p in perms.split(',') if p.strip()]
    return any(has_permission(user, perm) for perm in permission_list)
