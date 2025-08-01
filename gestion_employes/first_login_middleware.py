from django.shortcuts import redirect
from django.urls import reverse

class FirstLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Vérifier si l'utilisateur est connecté et n'a pas de secret 2FA
        if (request.user.is_authenticated and 
            hasattr(request.user, 'profile') and 
            not request.user.profile.two_factor_secret and
            request.path not in ['/gestion/login/otp/', '/gestion/logout/']):
            
            # Forcer la première configuration 2FA
            request.session['pending_user_id'] = request.user.id
            return redirect('gestion_employes:login_otp')
        
        return self.get_response(request)