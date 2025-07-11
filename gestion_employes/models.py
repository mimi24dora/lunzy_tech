import json
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Role(models.Model):
    ADMIN = 'admin'
    MANAGER = 'manager'
    RH = 'rh'
    EMPLOYE = 'employe'
    
    TYPE_CHOICES = [
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
        return self.nom
    
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
                for perm in perms:
                    permissions_display.append(f'{module.capitalize()}: {perm.capitalize()}')
            return ', '.join(permissions_display) if permissions_display else 'Aucune permission'
        except (json.JSONDecodeError, AttributeError, TypeError):
            return 'Aucune permission'

class Profile(models.Model):
    STATUT_CHOICES = (
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('conge', 'Congé'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    matricule = models.CharField(max_length=50, unique=True, null=True, blank=True)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    adresse = models.CharField(max_length=200, null=True, blank=True)
    date_embauche = models.DateField(null=True, blank=True)
    poste = models.CharField(max_length=100, null=True, blank=True)
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='actif',
        null=True,
        blank=True
    )
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    def get_statut_display(self):
        return dict(self.STATUT_CHOICES).get(self.statut, 'Non défini')
    
    def get_statut_badge(self):
        return {
            'actif': 'success',    # vert
            'inactif': 'danger',   # rouge
            'conge': 'warning'     # jaune
        }.get(self.statut, 'secondary')

class Pointage(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    heure_entree = models.TimeField()
    heure_sortie = models.TimeField(null=True, blank=True)
    remarques = models.TextField(blank=True)
    
    def __str__(self):
        return f"Pointage {self.profile.user.get_full_name()} - {self.date}"
