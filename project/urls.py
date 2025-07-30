from django.urls import path
from . import views

app_name = 'gestion_employes'

urlpatterns = [
    # Authentification
    path('', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    
    # 2FA URLs
    path('2fa/setup/', views.setup_2fa, name='setup_2fa'),
    path('2fa/verify/', views.verify_2fa, name='verify_2fa'),
    path('2fa/disable/', views.disable_2fa, name='disable_2fa'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Profil utilisateur
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Gestion des utilisateurs
    path('utilisateurs/', views.liste_utilisateurs, name='liste_utilisateurs'),
    path('utilisateurs/approve/<int:pk>/', views.approve_user, name='approve_user'),
    path('utilisateurs/reject/<int:pk>/', views.reject_user, name='reject_user'),
    
    # Rôles
    path('roles/', views.liste_roles, name='liste_roles'),
    path('roles/ajouter/', views.ajouter_role, name='ajouter_role'),
    path('roles/modifier/<int:pk>/', views.modifier_role, name='modifier_role'),
    path('roles/supprimer/<int:pk>/', views.supprimer_role, name='supprimer_role'),
    
    # Employés
    path('employes/', views.liste_employes, name='liste_employes'),
    
    # Pointage
    path('pointage/', views.pointage, name='pointage'),
    path('pointage/historique/', views.historique_pointages, name='historique_pointages'),
]