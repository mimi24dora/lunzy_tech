def modifier_utilisateur(request, pk):
    user = get_object_or_404(User, pk=pk)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = None
    
    roles = Role.objects.all()
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)
        role_id = request.POST.get('role')
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            
            # Sauvegarder ou créer le profil
            if profile:
                profile = profile_form.save()
            else:
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()
            
            # Mettre à jour le rôle du profil
            if role_id:
                role = get_object_or_404(Role, id=role_id)
                if hasattr(profile, 'role'):
                    profile.role = role
                    profile.save()
            
            messages.success(request, 'Utilisateur et profil mis à jour avec succès !')
            return redirect('gestion_employes:liste_utilisateurs')
        else:
            messages.error(request, 'Veuillez corriger les erreurs du formulaire.')
            return render(request, 'gestion_employes/utilisateurs/edit.html', {
                'user_form': user_form,
                'profile_form': profile_form,
                'user': user,
                'roles': roles
            })
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileForm(instance=profile)
        
    return render(request, 'gestion_employes/utilisateurs/edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'user': user,
        'roles': roles
    })
