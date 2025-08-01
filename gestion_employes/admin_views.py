from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy

class AdminLoginView(LoginView):
    template_name = 'admin/login.html'
    
    def get_success_url(self):
        # Rediriger vers l'admin après connexion réussie
        return '/admin/'
    
    def form_valid(self, form):
        user = form.get_user()
        # Vérifier que l'utilisateur a les droits staff
        if not user.is_staff:
            form.add_error(None, "Vous n'avez pas les droits d'accès à l'administration.")
            return self.form_invalid(form)
        return super().form_valid(form)