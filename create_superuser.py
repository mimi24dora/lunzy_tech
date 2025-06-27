from django.contrib.auth.models import User

# Créer un super utilisateur
User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='admin123'
)
