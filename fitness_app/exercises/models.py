from django.contrib.auth import get_user_model
from django.db import models
from enum import Enum

from django.utils import timezone

from fitness_app.clients.models import Client
from fitness_app.utils.mixins import ChoicesStringsMixin
from fitness_app.accounts.models import FitnessUser

User = get_user_model()


class ExerciseCategory(str, ChoicesStringsMixin, Enum):
    Гърди = "Гърди"
    Гръб = "Гръб"
    Рамо = "Рамо"
    Трицепс = "Трицепс"
    Крака = "Крака"
    Корем = "Корем"
    Кардио = "Кардио"
    Функционални = "Функционални"
    Аеробика = "Аеробика"
    Йога = "Йога"
    Пилатес = "Пилатес"


class Exercise(models.Model):
    MAX_LENGTH_EXERCISE_NAME = 100
    MAX_LENGTH_EQUIPMENT = 50

    name = models.CharField(
        max_length=MAX_LENGTH_EXERCISE_NAME,
        null=False,
        blank=False,
        verbose_name='Име'
    )

    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Описание'
    )

    category = models.CharField(
        max_length=ExerciseCategory.max_len(),
        choices=ExerciseCategory.choices(),
        null=True,
        blank=True,
        verbose_name='Категория'
    )

    equipment = models.CharField(
        max_length=MAX_LENGTH_EQUIPMENT,
        null=True,
        blank=True,
        verbose_name='Оборудване'
    )
    exercise_picture = models.ImageField(
        null=True,
        blank=True,
        verbose_name='Снимка на упражнението',
        upload_to='photos',
    )

    class Meta:
        verbose_name = 'Упражнение'
        verbose_name_plural = 'Упражнения'

    def __str__(self):
        return self.name


class CompletedExercise(models.Model):
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, verbose_name='Клиент')
    workout_exercise = models.ForeignKey('workouts.WorkoutExercise', on_delete=models.CASCADE, verbose_name='Упражнение')
    date = models.DateField(default=timezone.now, verbose_name='Дата за изпълнение')

    class Meta:
        verbose_name = 'Изпълнено упражнение'
        verbose_name_plural = 'Изпълнени упражнения'
        unique_together = ('client', 'workout_exercise', 'date')

    def __str__(self):
        return f"{self.client} - {self.workout_exercise} ({self.date})"