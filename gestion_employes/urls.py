from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from gestion_employes import views

app_name = 'gestion_employes'

urlpatterns = [
    path('register/', views.register, name='register'),
    # Authentication URLs
    path('login/', views.CustomLoginView.as_view(
        template_name='gestion_employes/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='gestion_employes:login'), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='gestion_employes/password_reset.html',
        email_template_name='gestion_employes/password_reset_email.html',
        success_url=reverse_lazy('gestion_employes:password_reset_done')
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='gestion_employes/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='gestion_employes/password_reset_confirm.html',
        success_url=reverse_lazy('gestion_employes:password_reset_complete')
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='gestion_employes/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Gestion des utilisateurs et profils
    path('utilisateurs/', views.liste_utilisateurs, name='liste_utilisateurs'),
    path('utilisateurs/<int:pk>/edit/', views.update_utilisateur, name='edit_utilisateur'),
    path('utilisateurs/<int:pk>/delete/', views.delete_utilisateur, name='delete_utilisateur'),
    path('utilisateurs/<int:pk>/view/', views.voir_utilisateur, name='view_utilisateur'),
    path('utilisateurs/<int:pk>/approve/', views.approve_user, name='approve_user'),
    path('utilisateurs/<int:pk>/reject/', views.reject_user, name='reject_user'),
    
    # Autres URLs
    path('', views.dashboard, name='dashboard'),
    path('employes/', views.liste_employes, name='liste_employes'),
    path('employes/ajouter/', views.ajouter_employe, name='ajouter_employe'),
    path('employes/<int:pk>/modifier/', views.modifier_profile, name='modifier_profile'),
    path('employes/<int:pk>/supprimer/', views.supprimer_profile, name='supprimer_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('pointage/', views.pointage, name='pointage'),
    path('historique/', views.historique_pointages, name='historique_pointages'),
    path('roles/', views.liste_roles, name='liste_roles'),
    path('roles/ajouter/', views.ajouter_role, name='ajouter_role'),
    path('roles/<int:pk>/modifier/', views.modifier_role, name='modifier_role'),
    path('roles/<int:pk>/supprimer/', views.supprimer_role, name='supprimer_role'),
    path('roles/<int:pk>/permissions/', views.gestion_permissions, name='gestion_permissions'),
    path('utilisateurs/<int:pk>/changer_role/', views.changer_role, name='changer_role'),
]
