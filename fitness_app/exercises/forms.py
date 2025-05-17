from django import forms

from fitness_app.exercises.models import Exercise


class ExerciseAddForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = "__all__"


class ExerciseEditForm(ExerciseAddForm):
    pass

class ExerciseDeleteForm(ExerciseAddForm):
    pass
