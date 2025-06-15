from django import forms
from django.forms import inlineformset_factory
from .models import ProgramExercise
from fitness_app.clients.models import Client

class ProgramExerciseForm(forms.ModelForm):
    class Meta:
        model = ProgramExercise
        fields = ['workout', 'date']
        widgets = {
            'workout': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

ProgramExerciseFormSet = inlineformset_factory(
    Client,
    ProgramExercise,
    form=ProgramExerciseForm,
    extra=1,
    can_delete=True,
)

ProgramExerciseFormEditSet = inlineformset_factory(
    Client,
    ProgramExercise,
    form=ProgramExerciseForm,
    extra=0,
    can_delete=True,
)
