from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse

class AdminApprovalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Super admin credentials
        SUPER_ADMIN_USERNAME = 'superadmin'
        SUPER_ADMIN_PASSWORD = 'SuperAdmin2025!'
        SUPER_ADMIN_EMAIL = 'superadmin@lunzytech.com'
        
        # Check if user is authenticated
        if request.user.is_authenticated:
            # Super admin access
            if (request.user.username == SUPER_ADMIN_USERNAME and 
                request.user.email == SUPER_ADMIN_EMAIL):
                # Super admin can access everything
                return self.get_response(request)
            
            # Regular user access
            if not request.user.is_active:
                # User needs approval
                if request.path != reverse('gestion_employes:login'):
                    messages.error(request, 'Votre compte n\'a pas encore été approuvé par l\'administrateur.')
                    return redirect('gestion_employes:login')
            
            # Restrict access to dashboard for non-approved users
            if request.path == reverse('gestion_employes:dashboard') and not request.user.is_active:
                messages.error(request, 'Votre compte n\'a pas encore été approuvé par l\'administrateur.')
                return redirect('gestion_employes:login')
        
        response = self.get_response(request)
        return response
