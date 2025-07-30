from django.contrib.auth.models import AbstractUser
from django.db import models
import pyotp
import qrcode
from io import BytesIO
import base64

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('editor', 'Éditeur'),
        ('viewer', 'Visualiseur'),
    ]
    
    # Champs 2FA
    totp_secret = models.CharField(max_length=32, blank=True)
    is_2fa_enabled = models.BooleanField(default=False)
    backup_codes = models.JSONField(default=list, blank=True)
    
    # Gestion des rôles
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    
    def generate_totp_secret(self):
        """Génère une clé secrète TOTP"""
        if not self.totp_secret:
            self.totp_secret = pyotp.random_base32()
            self.save()
        return self.totp_secret
    
    def get_totp_uri(self):
        """Génère l'URI pour le QR code"""
        return pyotp.totp.TOTP(self.totp_secret).provisioning_uri(
            name=self.email,
            issuer_name="Lunzy Tech"
        )
    
    def generate_qr_code(self):
        """Génère le QR code en base64"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(self.get_totp_uri())
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def verify_totp(self, token):
        """Vérifie le code TOTP"""
        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(token, valid_window=1)
    
    def has_permission(self, permission):
        """Vérifie les permissions selon le rôle"""
        permissions = {
            'admin': ['view', 'edit', 'delete', 'manage_users'],
            'editor': ['view', 'edit'],
            'viewer': ['view']
        }
        return permission in permissions.get(self.role, [])
    
    def can_access_section(self, section):
        """Vérifie l'accès aux sections selon le rôle"""
        access_map = {
            'admin': ['dashboard', 'users', 'roles', 'settings', 'reports'],
            'editor': ['dashboard', 'content', 'reports'],
            'viewer': ['dashboard', 'reports']
        }
        return section in access_map.get(self.role, [])