#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lunzy.settings')
django.setup()

from django.contrib.auth import get_user_model
from gestion_employes.models import Profile

User = get_user_model()

# Créer le superadmin
username = 'superadmin'
email = 'superadmin@lunzytech.com'
password = 'SuperAdmin2025!'

try:
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name='Super',
        last_name='Admin',
        is_active=True,
        is_staff=True,
        is_superuser=True
    )
    
    Profile.objects.create(
        user=user,
        telephone='',
        nom_entreprise='Lunzy Tech',
        statut='actif',
        approval_status='approved'
    )
    
    print(f"Superadmin créé avec succès!")
    print(f"Username: {username}")
    print(f"Password: {password}")
    
except Exception as e:
    print(f"Erreur: {e}")