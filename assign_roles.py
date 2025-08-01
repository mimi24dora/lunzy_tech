#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lunzy.settings')
django.setup()

from django.contrib.auth import get_user_model
from gestion_employes.models import Profile, Role

User = get_user_model()

# Créer les rôles s'ils n'existent pas
superadmin_role, _ = Role.objects.get_or_create(
    nom='superadmin', 
    defaults={'description': 'Super Administrateur avec tous les droits'}
)

directeur_role, _ = Role.objects.get_or_create(
    nom='DIRECTEUR_IT', 
    defaults={'description': 'Directeur IT avec tous les droits'}
)

# Assigner les rôles selon les postes
users_to_update = [
    ('chakam', superadmin_role),  # Super Administrateur
    ('kamy', directeur_role),     # dir IT -> Directeur IT
]

for username, role in users_to_update:
    try:
        user = User.objects.get(username=username)
        profile = user.profile
        profile.role = role
        profile.save()
        print(f"Rôle '{role.get_nom_display()}' assigné à {username}")
    except User.DoesNotExist:
        print(f"Utilisateur {username} non trouvé")
    except Exception as e:
        print(f"Erreur pour {username}: {e}")

print("Attribution des rôles terminée")