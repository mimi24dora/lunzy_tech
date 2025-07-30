from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from .ids import ids_monitor

class IDSMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip_address = self.get_client_ip(request)
        
        # Analyser les données de la requête
        request_data = {
            'GET': request.GET,
            'POST': request.POST,
            'path': request.path,
            'user_agent': request.META.get('HTTP_USER_AGENT', '')
        }
        
        # Détecter les attaques
        threats = ids_monitor.detect_attack(request_data, ip_address)
        
        if len(threats) >= 2:  # Seulement si plusieurs menaces détectées
            ids_monitor.block_ip(ip_address, f"Multiple threats: {', '.join(threats)}")
            return HttpResponseForbidden("Access denied - Security violation detected")
        
        return None
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip