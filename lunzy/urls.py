from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import reverse_lazy
from . import views as home_views
from gestion_employes.admin_views import AdminLoginView

# Personnaliser l'admin
admin.site.login = AdminLoginView.as_view()

urlpatterns = [
    path('', home_views.home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='admin/login.html'), name='login'),
    path('gestion/', include(('gestion_employes.urls', 'gestion_employes'), namespace='gestion_employes')),
    path('register/', include('accounts.urls')),
]