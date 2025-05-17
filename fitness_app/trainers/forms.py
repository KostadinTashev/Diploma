from django import forms
from django.contrib.auth.models import User

from fitness_app.trainers.models import Trainer


class TrainerForm(forms.ModelForm):
    class Meta:
        model = Trainer
        fields = ['speciality', 'years_of_experience', 'certifications', 'bio', 'phone_number']


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
