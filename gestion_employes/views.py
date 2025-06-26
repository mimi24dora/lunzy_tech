from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from .models import Employe, Pointage
from .forms import UserRegistrationForm, EmployeForm, PointageForm

# Vues d'authentification
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Compte créé avec succès !')
            return redirect('gestion_employes:login')
        else:
            messages.error(request, 'Veuillez corriger les erreurs du formulaire.')
    else:
        form = UserRegistrationForm()
    return render(request, 'gestion_employes/register.html', {
        'form': form,
        'title': 'Inscription'
    })



def user_logout(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté.')
    return redirect('login')

# Vues principales
@login_required
def dashboard(request):
    # Statistiques
    total_employes = Employe.objects.count()
    employes_actifs = Employe.objects.filter(statut='actif').count()
    pointages_jour = Pointage.objects.filter(date=timezone.now().date()).count()
    employes = Employe.objects.all()
    derniers_pointages = Pointage.objects.order_by('-date')[:5]
    
    context = {
        'total_employes': total_employes,
        'employes_actifs': employes_actifs,
        'pointages_jour': pointages_jour,
        'employes': employes,
        'derniers_pointages': derniers_pointages,
    }
    return render(request, 'gestion_employes/dashboard.html', context)

@login_required
def liste_employes(request):
    employes = Employe.objects.all()
    return render(request, 'gestion_employes/liste_employes.html', {'employes': employes})

@login_required
def ajouter_employe(request):
    if request.method == 'POST':
        form = EmployeForm(request.POST)
        if form.is_valid():
            employe = form.save(commit=False)
            employe.user = request.user
            employe.save()
            messages.success(request, 'Employé ajouté avec succès !')
            return redirect('liste_employes')
    else:
        form = EmployeForm()
    return render(request, 'gestion_employes/ajouter_employe.html', {'form': form})

@login_required
def pointage(request):
    if request.method == 'POST':
        form = PointageForm(request.POST)
        if form.is_valid():
            pointage = form.save(commit=False)
            pointage.date = timezone.now().date()
            pointage.save()
            messages.success(request, 'Pointage enregistré avec succès !')
            return redirect('dashboard')
    else:
        form = PointageForm()
    return render(request, 'gestion_employes/pointage.html', {'form': form})

@login_required
def historique_pointages(request):
    pointages = Pointage.objects.all().order_by('-date')
    return render(request, 'gestion_employes/historique_pointages.html', {'pointages': pointages})
