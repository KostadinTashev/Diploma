from django import forms
from django.contrib.auth import forms as auth_forms, get_user_model
from django.contrib.auth.forms import AuthenticationForm

UserModel = get_user_model()


class RegisterUserForm(auth_forms.UserCreationForm):
    class Meta:
        model = UserModel
        fields = ('username', 'email', 'password1', 'password2')

        labels = {
            'username': 'Потребителско име',
            'email': 'Имейл',
            'password1': 'Парола',
            'password2': 'Повторете паролата',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Потребителско име',
                'class': 'form-control',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Имейл',
                'class': 'form-control',
            }),

            'password1': forms.PasswordInput(attrs={
                'placeholder': 'Въведете парола',
            }),
            'password2': forms.PasswordInput(attrs={
                'placeholder': 'Повторете паролата',
            }),
        }




class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Потребителско име",
        widget=forms.TextInput(attrs={
            'placeholder': 'Въведете потребителско име',
            'class': 'form-control',
        })
    )

    password = forms.CharField(
        label="Парола",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Въведете парола',
            'class': 'form-control',
        })
    )
