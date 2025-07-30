#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lunzy.settings')
django.setup()

from gestion_employes.models import Profile

# Mettre à jour tous les profils sans matricule
profiles = Profile.objects.filter(matricule__isnull=True)
for profile in profiles:
    profile.save()  # Cela déclenchera la génération automatique du matricule
    print(f"Matricule généré pour {profile.user.username}: {profile.matricule}")

print(f"Matricules générés pour {profiles.count()} profils")