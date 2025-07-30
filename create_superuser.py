#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lunzy.settings')
django.setup()

from gestion_employes.models import CustomUser, Role, Profile

def create_superuser():
    # Vérifier si le superadmin existe déjà
    if CustomUser.objects.filter(username='superadmin').exists():
        print("Le superadmin existe déjà!")
        return
    
    # Créer le rôle superadmin
    superadmin_role, created = Role.objects.get_or_create(
        nom='superadmin',
        defaults={
            'description': 'Super Administrateur avec tous les droits',
            'permissions': {
                'gestion': ['tous'],
                'utilisateurs': ['tous'],
                'administration': ['tous']
            }
        }
    )
    
    # Créer le superutilisateur
    superuser = CustomUser.objects.create_superuser(
        username='superadmin',
        email='superadmin@lunzytech.com',
        password='SuperAdmin2025!',
        first_name='Super',
        last_name='Admin'
    )
    
    # Créer le profil associé
    Profile.objects.create(
        user=superuser,
        matricule='SUPER001',
        telephone='+243123456789',
        nom_entreprise='Lunzy Tech',
        poste='Super Administrateur',
        statut='actif',
        approval_status='approved',
        role=superadmin_role
    )
    
    print("Superadmin cree avec succes!")
    print("Username: superadmin")
    print("Email: superadmin@lunzytech.com")
    print("Password: SuperAdmin2025!")

if __name__ == '__main__':
    create_superuser()