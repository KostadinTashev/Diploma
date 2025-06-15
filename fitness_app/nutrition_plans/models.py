from django.db import models

from fitness_app.clients.models import Client


class NutritionPlan(models.Model):
    PLAN_NAME_MAX_LENGTH = 20

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='nutrition_plans',
        verbose_name='Клиент'
    )

    name = models.CharField(
        max_length=PLAN_NAME_MAX_LENGTH,
        null=False,
        blank=False,
        verbose_name='Име на хр. плана'
    )

    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Описание'
    )

    calories = models.PositiveIntegerField(
        null=False,
        blank=False,
        verbose_name='Калории'
    )

    carbohydrate = models.PositiveIntegerField(
        null=False,
        blank=False,
        verbose_name='Въглехидрати'
    )

    fats = models.PositiveIntegerField(
        null=False,
        blank=False,
        verbose_name='Мазнини'
    )

    proteins = models.PositiveIntegerField(
        null=False,
        blank=False,
        verbose_name='Протеини'
    )

    class Meta:
        verbose_name = 'Хранителен план'
        verbose_name_plural = 'Хранителни планове'

    def total_calories(self):
        return sum(meal.calories for meal in self.meals.all())

    def total_carbohydrates(self):
        return sum(meal.carbohydrate for meal in self.meals.all())

    def total_fats(self):
        return sum(meal.fats for meal in self.meals.all())

    def total_proteins(self):
        return sum(meal.proteins for meal in self.meals.all())

    def __str__(self):
        return f"{self.name} (Клиент: {self.client.user.full_name})"
