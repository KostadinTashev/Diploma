from django.db import models
from django.utils import timezone

from fitness_app.clients.models import Client
from fitness_app.exercises.models import Exercise
from fitness_app.workouts.models import Workout


class ProgramExercise(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name='Клиент'
    )
    workout = models.ForeignKey(
        Workout,
        on_delete=models.CASCADE,
        verbose_name='Тренировка'
    )
    date = models.DateField(
        null=False,
        blank=False,
        default=timezone.now,
        verbose_name='Дата'
    )

    class Meta:
        verbose_name = 'Упражнение в програмата'
        verbose_name_plural = 'Упражнения в програмата'
