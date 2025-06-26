from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Employe(models.Model):
    STATUT_CHOICES = (
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('conge', 'Congé'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    matricule = models.CharField(max_length=50, unique=True)
    telephone = models.CharField(max_length=20)
    adresse = models.CharField(max_length=200)
    date_embauche = models.DateField()
    poste = models.CharField(max_length=100)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='actif')
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Pointage(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    heure_entree = models.TimeField()
    heure_sortie = models.TimeField(null=True, blank=True)
    remarques = models.TextField(blank=True)
    
    def __str__(self):
        return f"Pointage {self.employe} - {self.date}"
