from django.shortcuts import redirect
from django.urls import reverse

class AdminRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Si l'utilisateur se connecte via l'admin et a les droits staff
        if (request.path == '/admin/login/' and 
            request.method == 'POST' and 
            request.user.is_authenticated and 
            request.user.is_staff):
            return redirect('/admin/')
            
        return response