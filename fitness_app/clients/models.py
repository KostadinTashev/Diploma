from enum import Enum

from django.db import models
from django.db.models import Q

from fitness_app.utils.mixins import ChoicesStringsMixin
from fitness_app.trainers.models import Trainer
from fitness_app.accounts.models import FitnessUser


class ClientGoals(str, ChoicesStringsMixin, Enum):
    ОТСЛАБВАНЕ = "Отслабване"
    МУСКУЛНА_МАСА = "Покачване на мускулна маса"
    СТЯГАНЕ = "Стягане и тонизиране"
    ИЗДРЪЖЛИВОСТ = "Подобряване на издръжливостта"
    СИЛА = "Повишаване на сила"
    ПОДДЪРЖАНЕ_НА_ТЕГЛО = "Поддържане на тегло"


class Client(models.Model):
    user = models.OneToOneField(
        FitnessUser,
        on_delete=models.CASCADE,
    )
    goals = models.CharField(
        max_length=ClientGoals.max_len(),
        choices=ClientGoals.choices(),
        null=True,
        blank=True,
        verbose_name='Цел'
    )

    trainer = models.ForeignKey(
        'trainers.Trainer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Треньор'
    )

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенти'

    def __str__(self):
        return f"Клиент: {self.user.full_name or self.user.username}"


class AppReview(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.client.user.email} - {self.rating}"


class TrainerReview(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.user.email} ➤ {self.trainer.user.email} - {self.rating}"


class TrainerRequest(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    trainer = models.ForeignKey('trainers.Trainer', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['client'],
                condition=Q(is_approved=False),
                name='unique_pending_request_per_client',
            )
        ]
        ordering = ['-created_at']