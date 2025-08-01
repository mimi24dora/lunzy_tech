#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lunzy.settings')
django.setup()

from django.contrib.auth import get_user_model
from gestion_employes.models import Profile
import pyotp

# Test de l'OTP
User = get_user_model()
try:
    user = User.objects.get(username='chakam')
    profile = user.profile
    
    print(f"Utilisateur: {user.username}")
    print(f"Email: {user.email}")
    print(f"Profil existe: {profile is not None}")
    
    if not profile.two_factor_secret:
        profile.two_factor_secret = pyotp.random_base32()
        profile.save()
        print("Secret OTP généré")
    
    print(f"Secret OTP: {profile.two_factor_secret}")
    
    # Générer un code de test
    totp = pyotp.TOTP(profile.two_factor_secret)
    current_code = totp.now()
    print(f"Code OTP actuel: {current_code}")
    
    # Vérifier le code
    is_valid = profile.verify_2fa_token(current_code)
    print(f"Code valide: {is_valid}")
    
except Exception as e:
    print(f"Erreur: {e}")