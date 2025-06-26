from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.urls import reverse_lazy

urlpatterns = [
    path('', lambda request: redirect('login', permanent=True)),  # Redirige vers la page de login
    path('admin/', admin.site.urls),
    path('gestion/', include(('gestion_employes.urls', 'gestion_employes'), namespace='gestion_employes')),
    path('', include('django.contrib.auth.urls')),  # URLs d'authentification par défaut
]