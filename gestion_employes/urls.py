from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = 'gestion_employes'

urlpatterns = [
    path('register/', views.register, name='register'),
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(
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
    
    # Gestion des utilisateurs
    path('utilisateurs/', views.view_user, name='view_user'),
    path('utilisateurs/ajouter/', views.ajouter_utilisateur, name='ajouter_utilisateur'),
    path('utilisateurs/<int:pk>/', views.voir_utilisateur, name='voir_utilisateur'),
    path('utilisateurs/<int:pk>/modifier/', views.modifier_utilisateur, name='modifier_utilisateur'),
    path('utilisateurs/<int:pk>/supprimer/', views.supprimer_utilisateur, name='supprimer_utilisateur'),
    
    # Autres URLs
    path('', views.dashboard, name='dashboard'),
    path('employes/', views.liste_employes, name='liste_employes'),
    path('employes/ajouter/', views.ajouter_employe, name='ajouter_employe'),
    path('pointage/', views.pointage, name='pointage'),
    path('historique/', views.historique_pointages, name='historique_pointages'),
]
