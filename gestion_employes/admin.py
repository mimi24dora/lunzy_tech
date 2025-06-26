from django.contrib import admin
from .models import Employe, Pointage

@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ('user', 'matricule', 'poste', 'statut', 'date_embauche')
    list_filter = ('statut', 'poste')
    search_fields = ('user__first_name', 'user__last_name', 'matricule')
    ordering = ('-date_embauche',)

@admin.register(Pointage)
class PointageAdmin(admin.ModelAdmin):
    list_display = ('employe', 'date', 'heure_entree', 'heure_sortie')
    list_filter = ('date', 'employe')
    search_fields = ('employe__user__first_name', 'employe__user__last_name')
    ordering = ('-date',)
