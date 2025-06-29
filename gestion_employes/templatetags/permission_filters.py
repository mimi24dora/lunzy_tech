from django import template
import json

register = template.Library()

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
    except (json.JSONDecodeError, AttributeError):
        return []

@register.filter
def has_permission(permissions, perm):
    """Vérifie si une permission est présente"""
    return perm in permissions
