#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lunzy.settings')
django.setup()

from django.contrib.auth import get_user_model
from gestion_employes.models import Profile

User = get_user_model()

# Corriger l'utilisateur kamy
try:
    user = User.objects.get(username='kamy')
    if hasattr(user, 'profile'):
        profile = user.profile
        if not profile.matricule:
            profile.matricule = None  # Forcer la régénération
        if not profile.poste:
            profile.poste = 'dir IT'
        profile.save()
        print(f"Matricule généré pour {user.username}: {profile.matricule}")
    else:
        profile = Profile.objects.create(
            user=user,
            telephone='',
            nom_entreprise='',
            statut='en_attente',
            approval_status='pending',
            poste='dir IT'
        )
        print(f"Profil créé pour {user.username} avec matricule: {profile.matricule}")
except User.DoesNotExist:
    print("Utilisateur kamy non trouvé")