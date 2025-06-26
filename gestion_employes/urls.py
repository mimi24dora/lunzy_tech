from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'gestion_employes'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='gestion_employes:login'), name='logout'),
    
    path('', views.dashboard, name='dashboard'),
    path('employes/', views.liste_employes, name='liste_employes'),
    path('employes/ajouter/', views.ajouter_employe, name='ajouter_employe'),
    path('pointage/', views.pointage, name='pointage'),
    path('historique/', views.historique_pointages, name='historique_pointages'),
]
