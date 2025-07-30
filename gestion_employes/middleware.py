from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
import logging

class AdminApprovalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('django.security')  # Pour enregistrer les alertes

    def __call__(self, request):
        # IDS simple : détection d'injection SQL ou script dans le corps de la requête
        suspicious_patterns = ["' OR 1=1", "'--", "<script>", "DROP TABLE", "UNION SELECT"]
        request_body = str(request.body).lower()
        for pattern in suspicious_patterns:
            if pattern.lower() in request_body:
                self.logger.warning(f"[ALERTE IDS] Requête suspecte détectée depuis {request.META.get('REMOTE_ADDR')} avec le motif : {pattern}")
                messages.error(request, "Comportement suspect détecté. La tentative a été enregistrée.")
                return redirect('gestion_employes:login')

        # Super admin credentials
        SUPER_ADMIN_USERNAME = 'superadmin'
        SUPER_ADMIN_PASSWORD = 'SuperAdmin2025!'
        SUPER_ADMIN_EMAIL = 'superadmin@lunzytech.com'
        
        # Check if user is authenticated
        if request.user.is_authenticated:
            # Super admin access
            if (request.user.username == SUPER_ADMIN_USERNAME and 
                request.user.email == SUPER_ADMIN_EMAIL):
                return self.get_response(request)
            
            # Regular user access
            if not request.user.is_active:
                if request.path != reverse('gestion_employes:login'):
                    messages.error(request, 'Votre compte n\'a pas encore été approuvé par l\'administrateur.')
                    return redirect('gestion_employes:login')
            
            if request.path == reverse('gestion_employes:dashboard') and not request.user.is_active:
                messages.error(request, 'Votre compte n\'a pas encore été approuvé par l\'administrateur.')
                return redirect('gestion_employes:login')
        
        response = self.get_response(request)
        return response
    
    'django_otp.middleware.OTPMiddleware',

