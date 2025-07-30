#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lunzy.settings')
django.setup()

from django.contrib.auth import get_user_model
from gestion_employes.models import Profile

User = get_user_model()

def activate_user(username):
    try:
        user = User.objects.get(username=username)
        user.is_active = True
        user.save()
        
        # Créer ou mettre à jour le profil
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'telephone': '',
                'nom_entreprise': '',
                'statut': 'actif',
                'approval_status': 'approved'
            }
        )
        if not created:
            profile.statut = 'actif'
            profile.approval_status = 'approved'
            profile.save()
        
        print(f"Utilisateur {username} activé avec succès!")
        
    except User.DoesNotExist:
        print(f"Utilisateur {username} non trouvé.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python activate_user.py <username>")
    else:
        activate_user(sys.argv[1])