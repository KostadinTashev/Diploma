from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(label='Име', max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Въведете вашето име',
        'id': 'name'
    }))
    email = forms.EmailField(label='Имейл', widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'example@domain.com',
        'id': 'email'
    }))
    message = forms.CharField(label='Съобщение', widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 4,
        'placeholder': 'Вашето съобщение...',
        'id': 'message'
    }))
