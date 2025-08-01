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

# Créer le rôle DIRECTEUR_IT s'il n'existe pas
role, created = Role.objects.get_or_create(
    nom='DIRECTEUR_IT', 
    defaults={'description': 'Directeur IT avec tous les droits'}
)
print(f"Rôle DIRECTEUR_IT: {'créé' if created else 'existe déjà'}")

# Créer un utilisateur directeur IT de test
user, created = User.objects.get_or_create(
    username='directeur_test',
    defaults={
        'email': 'directeur@lunzytech.com',
        'first_name': 'Test',
        'last_name': 'Directeur',
        'is_active': True
    }
)

if created:
    user.set_password('password123')
    user.save()
    print(f"Utilisateur créé: {user.username}")
else:
    print(f"Utilisateur existe déjà: {user.username}")

# Créer le profil avec le rôle DIRECTEUR_IT
profile, created = Profile.objects.get_or_create(
    user=user,
    defaults={
        'role': role,
        'statut': 'actif',
        'approval_status': 'approved',
        'poste': 'Directeur IT'
    }
)

if not created and profile.role != role:
    profile.role = role
    profile.save()

print(f"Profil: {'créé' if created else 'mis à jour'}")
print(f"Droits utilisateur - Staff: {user.is_staff}, Superuser: {user.is_superuser}")