from django import forms

from fitness_app.progress.models import Progress


class ProgressForm(forms.ModelForm):
    class Meta:
        model = Progress
        fields = ['weight', 'progress_date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }
