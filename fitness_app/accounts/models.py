from enum import Enum

from django.core.validators import MinLengthValidator
from django.db import models
from django.contrib.auth import models as auth_models

from fitness_app.utils.mixins import ChoicesStringsMixin


def validate_only_alphabetical(value):
    pass


class Gender(str, ChoicesStringsMixin, Enum):
    Мъж = 'Мъж'
    Жена = 'Жена'
    Друго = 'Друго'


class FitnessUser(auth_models.AbstractUser):
    MIN_FIRST_NAME_LENGTH = 2
    MAX_FIRST_NAME_LENGTH = 30
    MIN_LAST_NAME_LENGTH = 2
    MAX_LAST_NAME_LENGTH = 30
    first_name = models.CharField(
        max_length=MAX_FIRST_NAME_LENGTH,
        validators=(
            MinLengthValidator(MIN_FIRST_NAME_LENGTH),
            validate_only_alphabetical,
        ),
        verbose_name='Първо име'

    )
    last_name = models.CharField(
        max_length=MAX_LAST_NAME_LENGTH,
        validators=(
            MinLengthValidator(MIN_LAST_NAME_LENGTH),
            validate_only_alphabetical,
        ),
        verbose_name='Фамилно име'
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Имейл'
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата на раждане'
    )
    gender = models.CharField(
        choices=Gender.choices(),
        max_length=Gender.max_len(),
        verbose_name='Пол'
    )

    profile_picture = models.ImageField(
        null=True,
        blank=True,
        verbose_name='Профилна снимка',
        upload_to='photos',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Създаден на'
    )

    @property
    def full_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}"
        return None
