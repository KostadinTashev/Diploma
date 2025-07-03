from django import forms
from django.contrib.auth import forms as auth_forms, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm
from django.db import transaction
from django.forms import inlineformset_factory

from fitness_app.accounts.models import FitnessUser, Gender
from fitness_app.clients.models import Client
from fitness_app.meals.models import Meal, Product
from fitness_app.program_exercises.models import ProgramExercise
from fitness_app.trainers.models import Trainer, SpecialityType
from fitness_app.workouts.models import Workout, WorkoutExercise

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


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = FitnessUser
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']


class CustomUserCreationForm(UserCreationForm):
    make_admin = forms.BooleanField(  # ✔ отметка
        label="Администратор",
        required=False,
        help_text="Ако е маркирано – потребителят ще има пълен достъп.",
    )
    class Meta:
        model = FitnessUser
        fields = ['username', 'first_name', 'last_name', 'email', 'birth_date', 'gender', 'profile_picture',
                  'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
    def save(self, commit=True):
        user = super().save(commit=False)

        if self.cleaned_data.get("make_admin"):
            user.is_staff = True
            user.is_superuser = True

        if commit:
            user.save()

        return user

class CustomUserEditForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Нова парола",
        widget=forms.PasswordInput,
        required=False,
    )
    password2 = forms.CharField(
        label="Потвърди паролата",
        widget=forms.PasswordInput,
        required=False,
    )

    class Meta:
        model = FitnessUser
        fields = [
            'username', 'first_name', 'last_name', 'email', 'birth_date',
            'gender', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("Паролите не съвпадат.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class TrainerForm(CustomUserCreationForm):
    make_admin = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('make_admin', None)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
    speciality = forms.ChoiceField(
        choices=SpecialityType.choices(),
        label="Специалност",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    years_of_experience = forms.IntegerField(
        label="Години опит",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    certifications = forms.CharField(
        label="Сертификати",
        required=False,
    )
    bio = forms.CharField(
        label="Биография",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
    )
    phone_number = forms.CharField(
        label="Телефонен номер",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    class Meta(CustomUserCreationForm.Meta):
        model = CustomUserCreationForm.Meta.model
        fields = CustomUserCreationForm.Meta.fields + [
            "speciality",
            "years_of_experience",
            "certifications",
            "bio",
            "phone_number",
            'profile_picture',
        ]

    @transaction.atomic
    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()

        Trainer.objects.create(
            user=user,
            speciality=self.cleaned_data["speciality"],
            years_of_experience=self.cleaned_data["years_of_experience"],
            certifications=self.cleaned_data["certifications"],
            bio=self.cleaned_data["bio"],
            phone_number=self.cleaned_data["phone_number"],
        )
        return user

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #
    #     self.fields['user'].widget = forms.HiddenInput()

class TrainerAdminEditForm(forms.ModelForm):
    username       = forms.CharField(label="Потребителско име")
    first_name     = forms.CharField(label="Име",  required=False)
    last_name      = forms.CharField(label="Фамилия", required=False)
    email          = forms.EmailField(label="Имейл", required=False)
    birth_date     = forms.DateField(label="Дата на раждане", required=False,
                                     widget=forms.DateInput(attrs={"type": "date"}))
    gender = forms.ChoiceField(
        label="Пол",
        choices=Gender.choices(),
        required=False,
    )
    profile_picture = forms.ImageField(label="Профилна снимка", required=False)

    speciality            = forms.ChoiceField(
        label="Специалност",
        choices=SpecialityType.choices(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    years_of_experience   = forms.IntegerField(label="Години опит", min_value=0)
    certifications        = forms.CharField(label="Сертификати", required=False)
    bio                   = forms.CharField(label="Биография", required=False,
                                            widget=forms.Textarea(attrs={"rows": 3}))
    phone_number          = forms.CharField(label="Телефонен номер", required=False)

    class Meta:
        model  = Trainer
        fields = (
            "username", "first_name", "last_name", "email",
            "birth_date", "gender", "profile_picture",
            "speciality", "years_of_experience",
            "certifications", "bio", "phone_number",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        user = getattr(self.instance, "user", None)
        if user:
            self.fields["username"].initial        = user.username
            self.fields["first_name"].initial      = user.first_name
            self.fields["last_name"].initial       = user.last_name
            self.fields["email"].initial           = user.email
            self.fields["birth_date"].initial      = user.birth_date
            self.fields["gender"].initial          = user.gender
            self.fields["profile_picture"].initial = user.profile_picture

        # Бърз клас за Bootstrap
        for f in self.fields.values():
            f.widget.attrs.setdefault("class", "form-control")

    @transaction.atomic
    def save(self, commit=True):
        trainer = super().save(commit=False)   # полетата на Trainer

        # Актуализираме FitnessUser
        user = trainer.user
        user.username        = self.cleaned_data["username"]
        user.first_name      = self.cleaned_data["first_name"]
        user.last_name       = self.cleaned_data["last_name"]
        user.email           = self.cleaned_data["email"]
        user.birth_date      = self.cleaned_data["birth_date"]
        user.gender          = self.cleaned_data["gender"]
        if self.cleaned_data.get("profile_picture"):
            user.profile_picture = self.cleaned_data["profile_picture"]

        if commit:
            user.save()
            trainer.save()
        else:
            pass

        return trainer
class UserProfilePictureForm(forms.ModelForm):
    class Meta:
        model = FitnessUser
        fields = ['profile_picture']
        labels = {
            'profile_picture': 'Профилна снимка',
        }


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['goals', 'trainer']
        labels = {
            'goals': 'Цел на клиента',
            'trainer': 'Назначен треньор',
        }
        widgets = {
            'goals': forms.Select(attrs={'class': 'form-select'}),
            'trainer': forms.Select(attrs={'class': 'form-select'}),
        }


class MealAdminForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = [
            'client',
            'plan',
            'meal',
            'date',
            'description',
            'calories',
            'carbohydrate',
            'fats',
            'proteins',
        ]

        widgets = {
            'meal': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control'}),
            'carbohydrate': forms.NumberInput(attrs={'class': 'form-control'}),
            'fats': forms.NumberInput(attrs={'class': 'form-control'}),
            'proteins': forms.NumberInput(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'plan': forms.Select(attrs={'class': 'form-select'}),
        }

        labels = {
            'client': 'Клиент',
            'plan': 'План',
            'meal': 'Тип хранене',
            'date': 'Дата',
            'description': 'Описание',
            'calories': 'Калории',
            'carbohydrate': 'Въглехидрати',
            'fats': 'Мазнини',
            'proteins': 'Протеини',
        }


class WorkoutAdminForm(forms.ModelForm):
    class Meta:
        model  = Workout
        fields = ("program_name", "category", "description")

WorkoutExerciseFormAdminSet = inlineformset_factory(
    Workout,
    WorkoutExercise,
    fields=("exercise", "series", "repetitions", "rest_time"),
    extra=1,
    can_delete=True,
)

class ProgramExerciseAdminForm(forms.ModelForm):
    """Единична форма за CRUD (admin)."""
    class Meta:
        model = ProgramExercise
        fields = ("client", "workout", "date")
        widgets = {
            "client":  forms.Select(attrs={"class": "form-select"}),
            "workout": forms.Select(attrs={"class": "form-select"}),
            "date":    forms.DateInput(attrs={"type": "date",
                                              "class": "form-control"}),
        }
        labels = {
            "client":  "Клиент",
            "workout": "Тренировка",
            "date":    "Дата",
        }

from django import forms
class ProductForm(forms.ModelForm):
    class Meta:
        model  = Product
        fields = ['name', 'calories_per_100g', 'carbohydrates_per_100g',
                  'fats_per_100g', 'proteins_per_100g']