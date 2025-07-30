from django.urls import path, include
from . import views
from .views_login import custom_login



app_name = 'gestion_employes'

urlpatterns = [
    # Authentification
    path('', custom_login, name='login'),
    path('login/', custom_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),

    # 2FA
    path('2fa/setup/', views.setup_2fa, name='setup_2fa'),
    path('2fa/verify/', views.verify_2fa, name='verify_2fa'),
    path('2fa/disable/', views.disable_2fa, name='disable_2fa'),

    # Réinitialisation mot de passe
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset-complete/', views.password_reset_complete, name='password_reset_complete'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Profil utilisateur
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # Gestion des utilisateurs
    path('utilisateurs/', views.liste_utilisateurs, name='liste_utilisateurs'),
    path('utilisateurs/<int:pk>/edit/', views.edit_utilisateur, name='edit_utilisateur'),
    path('utilisateurs/<int:pk>/delete/', views.reject_user, name='delete_utilisateur'),
    path('utilisateurs/approve/<int:pk>/', views.approve_user, name='approve_user'),
    path('utilisateurs/reject/<int:pk>/', views.reject_user, name='reject_user'),

    # Rôles
    path('roles/', views.liste_roles, name='liste_roles'),
    path('roles/ajouter/', views.ajouter_role, name='ajouter_role'),
    path('roles/modifier/<int:pk>/', views.modifier_role, name='modifier_role'),
    path('roles/<int:pk>/permissions/', views.gestion_permissions, name='gestion_permissions'),
    path('roles/supprimer/<int:pk>/', views.supprimer_role, name='supprimer_role'),

    # Employés
    path('employes/', views.liste_employes, name='liste_employes'),
    path('employes/ajouter/', views.ajouter_employe, name='ajouter_employe'),
    path('employes/<int:pk>/modifier/', views.edit_utilisateur, name='modifier_profile'),
    path('employes/<int:pk>/supprimer/', views.reject_user, name='supprimer_profile'),

    # Pointage
    path('pointage/', views.pointage, name='pointage'),
    path('pointage/historique/', views.historique_pointages, name='historique_pointages'),
]
