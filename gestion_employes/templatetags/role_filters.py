from django import template

register = template.Library()

@register.filter
def has_role(user, role):
    """Vérifie si l'utilisateur a un rôle spécifique"""
    return user.role == role

@register.filter
def has_permission(user, permission):
    """Vérifie si l'utilisateur a une permission"""
    return user.has_permission(permission)

@register.filter
def can_access_section(user, section):
    """Vérifie si l'utilisateur peut accéder à une section"""
    return user.can_access_section(section)

@register.simple_tag
def user_sections(user):
    """Retourne les sections accessibles à l'utilisateur"""
    from ..views_2fa import get_user_sections
    return get_user_sections(user)