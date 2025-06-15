from django.db import models
from enum import Enum

from fitness_app.exercises.models import Exercise
from fitness_app.utils.mixins import ChoicesStringsMixin


class CategoryType(str, ChoicesStringsMixin, Enum):
    Бицепс = "Бицепс"
    Трицепс = "Трицепс"
    Гърди = "Гърди"
    Гръб = "Гръб"
    Рамо = "Рамо"


class Workout(models.Model):
    MAX_LENGTH_PROGRAM_NAME = 30

    program_name = models.CharField(
        max_length=MAX_LENGTH_PROGRAM_NAME,
        null=False,
        blank=False,
        verbose_name='Име'
    )

    category = models.CharField(
        max_length=CategoryType.max_len(),
        choices=CategoryType.choices(),
        null=False,
        blank=False,
        verbose_name='Категория'
    )

    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Описание'
    )

    class Meta:
        verbose_name = 'Тренировка'
        verbose_name_plural = 'Тренировки'

    def __str__(self):
        return f"{self.program_name}"


class WorkoutExercise(models.Model):
    workout = models.ForeignKey(
        Workout,
        on_delete=models.CASCADE,
        related_name='exercises',
        verbose_name='Тренировка'
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        verbose_name='Упражнение'
    )
    series = models.PositiveIntegerField(
        verbose_name='Серии'
    )
    repetitions = models.PositiveIntegerField(
        verbose_name='Повторения'
    )
    rest_time = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Почивка в секунди между сериите",
        verbose_name='Почивка между сериите'
    )

    class Meta:
        verbose_name = 'Упражнение в тренировка'
        verbose_name_plural = 'Упражнения в тренировка'

    def __str__(self):
        return f"{self.exercise.name} - {self.series}x{self.repetitions}"
