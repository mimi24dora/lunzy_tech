from django.contrib import admin
from .models import Profile, Pointage

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'matricule', 'poste', 'statut', 'date_embauche')
    list_filter = ('statut', 'poste')
    search_fields = ('user__first_name', 'user__last_name', 'matricule')
    ordering = ('-date_embauche',)

@admin.register(Pointage)
class PointageAdmin(admin.ModelAdmin):
    list_display = ('profile', 'date', 'heure_entree', 'heure_sortie')
    list_filter = ('date', 'profile')
    search_fields = ('profile__user__first_name', 'profile__user__last_name')
    ordering = ('-date',)
