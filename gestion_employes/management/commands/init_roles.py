from django.core.management.base import BaseCommand
from gestion_employes.models import Role

class Command(BaseCommand):
    help = 'Initialise les rôles par défaut dans la base de données'

    def handle(self, *args, **options):
        roles = {
            'admin': {
                'description': 'A accès à toutes les fonctionnalités du système',
                'permissions': {
                    'gestion_employes': ['add', 'change', 'delete', 'view'],
                    'pointage': ['add', 'change', 'delete', 'view'],
                    'rh': ['add', 'change', 'delete', 'view']
                }
            },
            'manager': {
                'description': 'Gère les employés et le pointage',
                'permissions': {
                    'gestion_employes': ['view', 'change'],
                    'pointage': ['add', 'change', 'view']
                }
            },
            'rh': {
                'description': 'Gère les ressources humaines',
                'permissions': {
                    'gestion_employes': ['add', 'change', 'view'],
                    'rh': ['add', 'change', 'view']
                }
            },
            'employe': {
                'description': 'Accès limité aux fonctionnalités de base',
                'permissions': {
                    'pointage': ['add', 'view']
                }
            }
        }

        for role_nom, role_data in roles.items():
            role, created = Role.objects.update_or_create(
                nom=role_nom,
                defaults={
                    'description': role_data['description'],
                    'permissions': role_data['permissions']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Créé le rôle: {role}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Mis à jour le rôle: {role}'))
