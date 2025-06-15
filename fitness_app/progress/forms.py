from django import forms

from fitness_app.progress.models import Progress


class ProgressForm(forms.ModelForm):
    class Meta:
        model = Progress
        fields = ['height', 'weight', 'neck', 'chest', 'waist', 'hip', 'progress_date']
        widgets = {
            'progress_date': forms.DateInput(attrs={'type': 'date'}),
            'height': forms.NumberInput(attrs={'placeholder': 'Височина'}),
            'weight': forms.NumberInput(attrs={'placeholder': 'Тегло'}),
            'neck': forms.NumberInput(attrs={'placeholder': 'Врат'}),
            'chest': forms.NumberInput(attrs={'placeholder': 'Гръдна обиколка'}),
            'waist': forms.NumberInput(attrs={'placeholder': 'Талия'}),
            'hip': forms.NumberInput(attrs={'placeholder': 'Ханш'}),
        }

class ProgressAddForm(forms.ModelForm):
    class Meta:
        model = Progress
        fields = ['height', 'weight', 'neck', 'chest', 'waist', 'hip', 'progress_date']
        widgets = {
            'progress_date': forms.DateInput(attrs={'type': 'date'}),
            'height': forms.NumberInput(attrs={'placeholder': 'Височина'}),
            'weight': forms.NumberInput(attrs={'placeholder': 'Тегло'}),
            'neck': forms.NumberInput(attrs={'placeholder': 'Врат'}),
            'chest': forms.NumberInput(attrs={'placeholder': 'Гръдна обиколка'}),
            'waist': forms.NumberInput(attrs={'placeholder': 'Талия'}),
            'hip': forms.NumberInput(attrs={'placeholder': 'Ханш'}),
        }