from enum import Enum
from django.db import models

from django.utils import timezone

from fitness_app.clients.models import Client
from fitness_app.nutrition_plans.models import NutritionPlan
from fitness_app.utils.mixins import ChoicesStringsMixin


class MealType(str, ChoicesStringsMixin, Enum):
    ЗАКУСКА = "Закуска"
    ОБЯД = "Обяд"
    ВЕЧЕРЯ = "Вечеря"
    СНАКС = "Снакс / междинно хранене"


class Meal(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Клиент'
    )
    plan = models.ForeignKey(
        NutritionPlan,
        on_delete=models.CASCADE,
        related_name='meals',
        null=True,
        blank=True,
        verbose_name='Хранителен план'
    )

    meal = models.CharField(
        choices=MealType.choices(),
        max_length=MealType.max_len(),
        null=False,
        blank=False,
        verbose_name='Тип хранене'
    )
    date = models.DateField(
        null=True,
        blank=True,
        default=timezone.now,
        verbose_name='Дата'
    )

    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Описание'
    )

    calories = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Калории'
    )

    carbohydrate = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Въглехидрати'
    )

    fats = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Мазнини'
    )

    proteins = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Протеини'
    )

    class Meta:
        verbose_name = 'Хранене'
        verbose_name_plural = 'Хранения'


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Име")
    calories_per_100g = models.FloatField(null=True, blank=True, verbose_name="Калории на 100 грама")
    carbohydrates_per_100g = models.FloatField(null=True, blank=True, verbose_name='Въглехидрати на 100 грама')
    fats_per_100g = models.FloatField(null=True, blank=True, verbose_name="Мазнини на 100 грама")
    proteins_per_100g = models.FloatField(null=True, blank=True, verbose_name='Протеини на 100 грама')
    serving_size = models.CharField(max_length=50, null=True, blank=True, verbose_name='Размер на порция')

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукти'

    def __str__(self):
        return self.name


class FoodItem(models.Model):
    meal = models.ForeignKey(
        Meal,
        on_delete=models.CASCADE,
        related_name='food_items',
        verbose_name='Хранене'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Продукт'
    )

    quantity = models.FloatField(
        help_text="Количество в грамове",
        null=False,
        blank=False,
        verbose_name='Количество в грамове'
    )

    class Meta:
        verbose_name = 'Хранителен продукт'
        verbose_name_plural = 'Хранителни продукти'

    def __str__(self):
        return f"{self.product.name} ({self.quantity}g)"

    def get_calories(self):
        return round((self.product.calories_per_100g / 100) * self.quantity, 2)

    def get_carbohydrates(self):
        return round((self.product.carbohydrates_per_100g / 100) * self.quantity, 2)

    def get_fats(self):
        return round((self.product.fats_per_100g / 100) * self.quantity, 2)

    def get_proteins(self):
        return round((self.product.proteins_per_100g / 100) * self.quantity, 2)
