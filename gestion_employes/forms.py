from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Profile, Role, Pointage

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Entrez votre email'
    }))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Prénom'
    }))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nom'
    }))
    telephone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Numéro de téléphone'
    }))
    nom_entreprise = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nom de l\'entreprise'
    }))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom d\'utilisateur'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmez le mot de passe'
        })

class TwoFactorSetupForm(forms.Form):
    token = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '000000',
            'maxlength': '6',
            'style': 'font-size: 1.5em; letter-spacing: 0.5em;'
        }),
        label="Code de vérification"
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_token(self):
        token = self.cleaned_data.get('token')
        if not self.user.verify_2fa_token(token):
            raise forms.ValidationError("Code invalide. Veuillez réessayer.")
        return token

class TwoFactorVerifyForm(forms.Form):
    token = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '000000',
            'maxlength': '6',
            'style': 'font-size: 1.5em; letter-spacing: 0.5em;',
            'autocomplete': 'off'
        }),
        label="Code de vérification"
    )
    
    backup_code = forms.CharField(
        max_length=9,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '0000-0000',
            'style': 'font-size: 1.2em; letter-spacing: 0.2em;'
        }),
        label="Code de récupération"
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        token = cleaned_data.get('token')
        backup_code = cleaned_data.get('backup_code')

        if not token and not backup_code:
            raise forms.ValidationError("Veuillez entrer un code de vérification ou un code de récupération.")

        if token and not self.user.verify_2fa_token(token):
            if backup_code and not self.user.verify_backup_code(backup_code):
                raise forms.ValidationError("Code invalide. Veuillez réessayer.")
        
        return cleaned_data

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['telephone', 'nom_entreprise', 'adresse', 'date_embauche', 'poste', 'statut', 'role']
        widgets = {
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'nom_entreprise': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'poste': forms.TextInput(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['nom', 'description']
        widgets = {
            'nom': forms.Select(choices=Role.TYPE_CHOICES, attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class EmployeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['telephone', 'nom_entreprise', 'adresse', 'date_embauche', 'poste', 'statut', 'role']
        widgets = {
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'nom_entreprise': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'poste': forms.TextInput(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }

class PointageForm(forms.ModelForm):
    class Meta:
        model = Pointage
        fields = ['profile', 'heure_entree', 'heure_sortie', 'remarques']
        widgets = {
            'profile': forms.Select(attrs={'class': 'form-control'}),
            'heure_entree': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'heure_sortie': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'remarques': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }