from enum import Enum
from django.db import models
from django.core.validators import MinLengthValidator
from django.conf import settings

from fitness_app.utils.mixins import ChoicesStringsMixin


class SpecialityType(str, ChoicesStringsMixin, Enum):
    СИЛОВА = "Силова тренировка"
    АЕРОБИКА = "Аеробика"
    ЙОГА = "Йога"
    КРОСФИТ = "Кросфит"
    ДРУГО = "Друго"


class Trainer(models.Model):
    PHONE_NUMBER_MIN_LENGTH = 10
    PHONE_NUMBER_MAX_LENGTH = 13
    user = models.OneToOneField(
        'accounts.FitnessUser',
        on_delete=models.CASCADE,
    )

    speciality = models.CharField(
        choices=SpecialityType.choices(),
        max_length=SpecialityType.max_len(),
        null=False,
        blank=False,
        verbose_name='Специалност',
    )

    years_of_experience = models.PositiveIntegerField(
        null=False,
        blank=False,
        verbose_name='Години опит',
    )

    certifications = models.TextField(
        null=True,
        blank=True,
        verbose_name='Сертификати',

    )

    bio = models.TextField(
        null=True,
        blank=True,
        verbose_name='Био',
    )

    phone_number = models.CharField(
        max_length=PHONE_NUMBER_MAX_LENGTH,
        validators=(
            MinLengthValidator(PHONE_NUMBER_MIN_LENGTH),
        ),
        unique=True,
        verbose_name='Телефонен номер',
    )

    class Meta:
        verbose_name = "Треньор"
        verbose_name_plural = "Треньори"

    def __str__(self):
        return f"Треньор: {self.user.full_name or self.user.username}"
