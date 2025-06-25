from django import forms
from django.contrib.auth import get_user_model

from .models import Client, ClientGoals
from ..trainers.models import Trainer

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
class ChangeTrainerForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['trainer']
        labels = {'trainer': 'Избери треньор'}
        widgets = {
            'trainer': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['trainer'].queryset = Trainer.objects.select_related('user').order_by('user__first_name')

class ClientEditForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['first_name', 'last_name', 'email', 'birth_date', 'gender', 'profile_picture']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
