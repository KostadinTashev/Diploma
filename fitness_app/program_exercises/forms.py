# forms.py
from django import forms
from django.forms import inlineformset_factory, modelformset_factory
from .models import ProgramExercise

class ProgramExerciseForm(forms.ModelForm):
    class Meta:
        model = ProgramExercise
        fields = ['workout', 'day_of_week']
        widgets = {
            'workout': forms.Select(attrs={'class': 'form-select'}),
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
        }

ProgramExerciseFormSet = modelformset_factory(
    ProgramExercise,
    fields=('workout', 'day_of_week'),
    extra=1,
    can_delete=True,
)
