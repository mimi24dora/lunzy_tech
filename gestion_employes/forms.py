from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Pointage, Role

class EmployeForm(forms.ModelForm):
    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone', '')
        if not telephone.isdigit():
            raise forms.ValidationError('Le numéro doit contenir uniquement des chiffres.')
        if len(telephone) != 10:
            raise forms.ValidationError('Le numéro doit contenir exactement 10 chiffres.')
        return telephone

    class Meta:
        model = Profile
        fields = ['matricule', 'telephone', 'poste', 'statut', 'role']
        widgets = {
            'telephone': forms.TextInput(attrs={
                'maxlength': '10',
                'pattern': '\\d{10}',
                'inputmode': 'numeric',
                'placeholder': 'Ex: 0612345678',
                'class': 'form-control',
            }),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'votre@email.com'
    }))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Votre prénom'
    }))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Votre nom'
    }))
    telephone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 0612345678',
            'pattern': '\d{10}',
            'inputmode': 'numeric',
            'maxlength': '10'
        }),
        help_text="Format: 10 chiffres sans espace ni caractère spécial"
    )
    nom_entreprise = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Le nom de votre entreprise'
        }),
        help_text="Le nom de l'entreprise pour laquelle vous travaillez"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'telephone', 'nom_entreprise', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choisissez un nom d\'utilisateur'}),
        }
    
    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone', '')
        if not telephone.isdigit():
            raise forms.ValidationError('Le numéro doit contenir uniquement des chiffres.')
        if len(telephone) != 10:
            raise forms.ValidationError('Le numéro doit contenir exactement 10 chiffres.')
        return telephone

class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['matricule', 'telephone', 'poste', 'statut', 'role']
        widgets = {
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

class PointageForm(forms.ModelForm):
    TYPE_CHOICES = [
        ('ENTREE', 'Entrée'),
        ('SORTIE', 'Sortie'),
    ]
    
    type = forms.ChoiceField(choices=TYPE_CHOICES, widget=forms.RadioSelect)
    
    class Meta:
        model = Pointage
        fields = ['profile', 'type']
        widgets = {
            'profile': forms.Select(attrs={'class': 'form-select'}),
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'})
        }

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['nom', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
