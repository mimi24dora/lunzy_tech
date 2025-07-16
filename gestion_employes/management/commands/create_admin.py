from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Crée un super utilisateur administrateur'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='superadmin',
                email='superadmin@lunzytech.com',
                password='SuperAdmin2025!'
            )
            self.stdout.write(self.style.SUCCESS('Super utilisateur créé avec succès'))
        else:
            self.stdout.write(self.style.WARNING('Super utilisateur déjà existant'))
