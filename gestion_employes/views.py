from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, logout, get_user_model
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from .models import Employe, Pointage
from .forms import UserRegistrationForm, EmployeForm, PointageForm, UserUpdateForm

User = get_user_model()

# Vues d'authentification
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.')
            return redirect('gestion_employes:login')
        else:
            messages.error(request, 'Veuillez corriger les erreurs du formulaire.')
    else:
        form = UserRegistrationForm()
    return render(request, 'gestion_employes/register.html', {
        'form': form,
        'title': 'Inscription'
    })

@login_required
@require_http_methods(['GET'])
def user_logout(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté.')
    return redirect('gestion_employes:login')

# Vues de gestion des utilisateurs
@login_required
def view_user(request):
    utilisateurs = User.objects.all()
    return render(request, 'gestion_employes/utilisateurs/view_user.html', {
        'utilisateurs': utilisateurs
    })

@login_required
def modifier_utilisateur(request, pk):
    user = get_object_or_404(User, pk=pk)
    employe = get_object_or_404(Employe, user=user)
    
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST, instance=user)
        employe_form = EmployeForm(request.POST, instance=employe)
        
        if user_form.is_valid() and employe_form.is_valid():
            user_form.save()
            employe_form.save()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Utilisateur et employé mis à jour avec succès !'})
            
            messages.success(request, 'Utilisateur et employé mis à jour avec succès !')
            return redirect('gestion_employes:view_user')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': user_form.errors | employe_form.errors})
            
            messages.error(request, 'Veuillez corriger les erreurs du formulaire.')
    else:
        user_form = UserRegistrationForm(instance=user)
        employe_form = EmployeForm(instance=employe)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'gestion_employes/utilisateurs/form_modifier.html', {
            'user_form': user_form,
            'employe_form': employe_form,
            'user': user
        })
    
    return render(request, 'gestion_employes/utilisateurs/view_user.html', {
        'user_form': user_form,
        'employe_form': employe_form,
        'user': user
    })

@login_required
def voir_utilisateur(request, pk):
    user = get_object_or_404(User, pk=pk)
    employe = user.employe if hasattr(user, 'employe') else None
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        employe_form = EmployeForm(request.POST, instance=employe) if employe else EmployeForm(request.POST)
        
        if user_form.is_valid() and employe_form.is_valid():
            user = user_form.save()
            employe = employe_form.save(commit=False)
            employe.user = user
            employe.save()
            
            messages.success(request, 'Utilisateur et employé mis à jour avec succès !')
            return redirect('gestion_employes:view_user')
        else:
            messages.error(request, 'Veuillez corriger les erreurs du formulaire.')
    else:
        user_form = UserUpdateForm(instance=user)
        employe_form = EmployeForm(instance=employe) if employe else EmployeForm()
    
    return render(request, 'gestion_employes/utilisateurs/modifier.html', {
        'user_form': user_form,
        'employe_form': employe_form,
        'user': user,
        'employe': employe
    })

@login_required
def voir_utilisateur(request, pk):
    user = get_object_or_404(User, pk=pk)
    employe = user.employe if hasattr(user, 'employe') else None
    pointages = Pointage.objects.filter(employe=employe).order_by('-date') if employe else None
    
    context = {
        'user': user,
        'employe': employe,
        'pointages': pointages,
        'est_super_admin': request.user.is_superuser
    }
    return render(request, 'gestion_employes/utilisateurs/detail.html', context)

@login_required
def supprimer_utilisateur(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Utilisateur supprimé avec succès !')
        return redirect('gestion_employes:view_user')
    
    return render(request, 'gestion_employes/utilisateurs/supprimer.html', {
        'user': user
    })

@login_required
def ajouter_utilisateur(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        employe_form = EmployeForm(request.POST)
        
        if user_form.is_valid() and employe_form.is_valid():
            user = user_form.save()
            employe = employe_form.save(commit=False)
            employe.user = user
            employe.save()
            
            messages.success(request, 'Utilisateur et employé créés avec succès !')
            return redirect('gestion_employes:view_user')
        else:
            messages.error(request, 'Veuillez corriger les erreurs du formulaire.')
    else:
        user_form = UserRegistrationForm()
        employe_form = EmployeForm()
    
    return render(request, 'gestion_employes/utilisateurs/ajouter.html', {
        'user_form': user_form,
        'employe_form': employe_form
    })

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
