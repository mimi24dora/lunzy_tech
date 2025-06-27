from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.urls import reverse_lazy
from . import views as home_views

urlpatterns = [
    path('', home_views.home, name='home'),  # Home page
    path('admin/', admin.site.urls),
    path('gestion/', include(('gestion_employes.urls', 'gestion_employes'), namespace='gestion_employes')),
]