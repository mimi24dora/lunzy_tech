import logging
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Profile

logger = logging.getLogger(__name__)

class IDSMonitor:
    def __init__(self):
        self.suspicious_patterns = {
            'sql_injection': ['union select', 'drop table', 'insert into', 'delete from', "'; drop"],
            'xss': ['<script>alert', 'javascript:alert', 'onerror=alert'],
            'path_traversal': ['../../../etc/passwd', '..\\..\\windows']
        }
    
    def detect_attack(self, request_data, ip_address):
        """Détecte les tentatives d'attaque"""
        threats = []
        
        for attack_type, patterns in self.suspicious_patterns.items():
            for pattern in patterns:
                if pattern.lower() in str(request_data).lower():
                    threats.append(attack_type)
                    logger.warning(f"IDS Alert: {attack_type} detected from {ip_address}")
        
        return threats
    
    def block_ip(self, ip_address, reason):
        """Bloque une IP suspecte"""
        User = get_user_model()
        try:
            users = User.objects.filter(last_login_ip=ip_address)
            for user in users:
                user.account_locked_until = timezone.now() + timezone.timedelta(hours=24)
                user.save()
            logger.critical(f"IP {ip_address} blocked: {reason}")
        except Exception as e:
            logger.error(f"Error blocking IP {ip_address}: {e}")

ids_monitor = IDSMonitor()