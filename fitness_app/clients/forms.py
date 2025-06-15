from django import forms
from django.contrib.auth import get_user_model

from .models import Client, ClientGoals

UserModel = get_user_model()


class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['first_name', 'last_name', 'birth_date', 'email', 'gender', 'profile_picture']



class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['goals', ]
        widgets = {
            'goals': forms.Select(choices=ClientGoals.choices()),

        }


class ClientEditForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['first_name', 'last_name', 'email', 'birth_date', 'gender', 'profile_picture']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
