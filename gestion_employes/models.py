import json
import pyotp
import qrcode
from io import BytesIO
import base64
import secrets

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
from django.core.files.base import ContentFile


class CustomUser(AbstractUser):
    """Modèle utilisateur personnalisé avec support 2FA"""
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=50, blank=True, null=True)
    
    # Champs 2FA
    is_2fa_enabled = models.BooleanField(default=False, verbose_name="2FA activé")
    two_factor_secret = models.CharField(
        max_length=32, 
        blank=True, 
        null=True,
        verbose_name="Clé secrète 2FA"
    )
    backup_codes = models.JSONField(
        default=list, 
        blank=True,
        verbose_name="Codes de récupération"
    )
    
    # Champs sécurité
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.username

    def generate_2fa_secret(self):
        """Génère une nouvelle clé secrète pour le 2FA"""
        if not self.two_factor_secret:
            self.two_factor_secret = pyotp.random_base32()
            self.save()
        return self.two_factor_secret
    
    def get_2fa_uri(self):
        """Génère l'URI pour le QR code Google Authenticator"""
        if not self.two_factor_secret:
            self.generate_2fa_secret()
        
        return pyotp.totp.TOTP(self.two_factor_secret).provisioning_uri(
            name=self.email,
            issuer_name="Gestion Employés - LunzyTech"
        )
    
    def generate_qr_code(self):
        """Génère le QR code en base64 pour l'affichage"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(self.get_2fa_uri())
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def verify_2fa_token(self, token):
        """Vérifie le token 2FA"""
        if not self.two_factor_secret:
            return False
        
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.verify(token, valid_window=1)
    
    def generate_backup_codes(self):
        """Génère des codes de récupération"""
        codes = []
        for _ in range(10):
            code = ''.join([str(secrets.randbelow(10)) for _ in range(8)])
            codes.append(f"{code[:4]}-{code[4:]}")
        
        self.backup_codes = codes
        self.save()
        return codes
    
    def verify_backup_code(self, code):
        """Vérifie et utilise un code de récupération"""
        if code in self.backup_codes:
            self.backup_codes.remove(code)
            self.save()
            return True
        return False
    
    def reset_failed_login_attempts(self):
        """Remet à zéro les tentatives de connexion échouées"""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.save()
    
    def increment_failed_login_attempts(self):
        """Incrémente les tentatives de connexion échouées"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.account_locked_until = timezone.now() + timezone.timedelta(minutes=30)
        self.save()
    
    def is_account_locked(self):
        """Vérifie si le compte est verrouillé"""
        if self.account_locked_until:
            if timezone.now() < self.account_locked_until:
                return True
            else:
                self.reset_failed_login_attempts()
        return False


class Role(models.Model):
    ADMIN = 'admin'
    MANAGER = 'manager'
    RH = 'rh'
    EMPLOYE = 'employe'
    
    TYPE_CHOICES = [
        ('superadmin', 'Super Administrateur'),
        (ADMIN, 'Administrateur'),
        (MANAGER, 'Manager'),
        (RH, 'Ressources Humaines'),
        (EMPLOYE, 'Employé'),
    ]
    
    nom = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    permissions = models.JSONField(default=dict)
    date_creation = models.DateTimeField(default=timezone.now)
    date_modification = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.nom
    
    def get_nom_display(self):
        """Renvoie le nom complet du rôle"""
        return dict(self.TYPE_CHOICES).get(self.nom, self.nom)
    
    class Meta:
        verbose_name = 'Rôle'
        verbose_name_plural = 'Rôles'
        ordering = ['nom']
    
    def get_permissions_display(self):
        """Renvoie une représentation lisible des permissions"""
        try:
            permissions = self.permissions if isinstance(self.permissions, dict) else json.loads(self.permissions)
            permissions_display = []
            for module, perms in permissions.items():
                if isinstance(perms, dict):
                    for perm, enabled in perms.items():
                        if enabled:  # Seulement si la permission est activée
                            permissions_display.append(f'{module.capitalize()}: {perm.capitalize()}')
                else:
                    for perm in perms:
                        permissions_display.append(f'{module.capitalize()}: {perm.capitalize()}')
            return ', '.join(permissions_display) if permissions_display else 'Aucune permission'
        except (json.JSONDecodeError, AttributeError, TypeError):
            return 'Aucune permission'


class Profile(models.Model):
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('conge', 'Congé'),
        ('en_attente', 'En attente d\'approbation'),
    ]
    
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    matricule = models.CharField(max_length=50, unique=True, null=True, blank=True)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    nom_entreprise = models.CharField(max_length=100, verbose_name="Nom de l'entreprise", null=True, blank=True)
    adresse = models.CharField(max_length=200, null=True, blank=True)
    date_embauche = models.DateField(null=True, blank=True)
    poste = models.CharField(max_length=100, null=True, blank=True)
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente',
        null=True,
        blank=True
    )
    
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='pending',
        null=True,
        blank=True
    )
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Champs 2FA
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    def get_statut_display(self):
        return dict(self.STATUT_CHOICES).get(self.statut, 'Non défini')
    
    def get_statut_badge(self):
        return {
            'actif': 'success',
            'inactif': 'danger',
            'conge': 'warning',
            'en_attente': 'info'
        }.get(self.statut, 'secondary')

    def get_approval_status_badge(self):
        return {
            'pending': 'info',
            'approved': 'success',
            'rejected': 'danger'
        }.get(self.approval_status, 'secondary')

    def save(self, *args, **kwargs):
        # Générer le matricule automatiquement
        if not self.matricule:
            if self.user.username == 'superadmin':
                self.matricule = 'SUPER001'
            else:
                # Générer un matricule unique
                import random
                import string
                while True:
                    matricule = 'EMP' + ''.join(random.choices(string.digits, k=4))
                    if not Profile.objects.filter(matricule=matricule).exists():
                        self.matricule = matricule
                        break
        
        # Gérer les rôles
        if self.user.username == 'superadmin':
            if not self.role_id:
                try:
                    self.role = Role.objects.get(nom='superadmin')
                except Role.DoesNotExist:
                    superadmin_role = Role.objects.create(
                        nom='superadmin',
                        description='Super Administrateur avec tous les droits',
                        permissions={
                            'gestion': ['tous'],
                            'utilisateurs': ['tous'],
                            'administration': ['tous']
                        }
                    )
                    self.role = superadmin_role
        
        super().save(*args, **kwargs)
    
    def get_approval_status_display(self):
        return dict(self.APPROVAL_STATUS_CHOICES).get(self.approval_status, 'Non défini')


class Pointage(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    heure_entree = models.TimeField()
    heure_sortie = models.TimeField(null=True, blank=True)
    remarques = models.TextField(blank=True)
    
    def __str__(self):
        return f"Pointage {self.profile.user.get_full_name()} - {self.date}"
