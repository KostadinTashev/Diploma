# forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Workout, WorkoutExercise

class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['program_name', 'category', 'description']
        widgets = {
            'program_name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

class WorkoutExerciseForm(forms.ModelForm):
    class Meta:
        model = WorkoutExercise
        fields = ['exercise', 'series', 'repetitions', 'rest_time']
        widgets = {
            'exercise': forms.Select(attrs={'class': 'form-control'}),
            'series': forms.NumberInput(attrs={'class': 'form-control'}),
            'repetitions': forms.NumberInput(attrs={'class': 'form-control'}),
            'rest_time': forms.NumberInput(attrs={'class': 'form-control'}),
        }

WorkoutExerciseFormSet = inlineformset_factory(
    Workout, WorkoutExercise, form=WorkoutExerciseForm,
    extra=1, can_delete=True
)
