from django import forms
from django.contrib.auth import get_user_model

from .models import Client, ClientGoals

UserModel = get_user_model()


class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['first_name', 'last_name', 'birth_date', 'gender', 'profile_picture']


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['goals', 'height', 'weight', 'neck', 'chest', 'waist', 'hip']
        widgets = {
            'goals': forms.Select(choices=ClientGoals.choices()),
            'height': forms.NumberInput(attrs={'placeholder': 'Височина'}),
            'weight': forms.NumberInput(attrs={'placeholder': 'Тегло'}),
            'neck': forms.NumberInput(attrs={'placeholder': 'Врат'}),
            'chest': forms.NumberInput(attrs={'placeholder': 'Гръдна обиколка'}),
            'waist': forms.NumberInput(attrs={'placeholder': 'Талия'}),
            'hip': forms.NumberInput(attrs={'placeholder': 'Ханш'}),
        }


class ClientEditForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['first_name', 'last_name', 'email', 'birth_date', 'gender', 'profile_picture']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
