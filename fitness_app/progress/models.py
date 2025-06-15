from django.db import models
from django.utils import timezone

from fitness_app.clients.models import Client


class Progress(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name='Клиент'
    )

    progress_date = models.DateField(
        null=False,
        blank=False,
        verbose_name='Дата',
        default=timezone.now
    )

    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=False,
        blank=False,
        verbose_name='Тегло (кг)'
    )

    height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Височина (см)'
    )

    neck = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Врат (см)'
    )

    chest = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Гръдна обиколка (см)'
    )

    waist = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Талия (см)'
    )

    hip = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Ханш (см)'
    )

    muscle_mass = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Мускулна маса (%)'
    )

    body_fat_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Подкожни мазнини (%)'
    )

    class Meta:
        verbose_name = 'Прогрес'
        verbose_name_plural = 'Прогреси'

    def __str__(self):
        return f"{self.client.user.full_name} – {self.progress_date}"
