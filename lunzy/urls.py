from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import reverse_lazy
from . import views as home_views

urlpatterns = [
    path('', home_views.home, name='home'),  # Home page
    path('admin/', admin.site.urls),
    path('gestion/', include(('gestion_employes.urls', 'gestion_employes'), namespace='gestion_employes')),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', include('accounts.urls')),
]