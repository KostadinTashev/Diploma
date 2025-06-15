from django.contrib import admin
from .models import Meal, Product, FoodItem


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = (
        'client_full_name',
        'plan_name',
        'meal',
        'date',
        'calories',
        'carbohydrate',
        'fats',
        'proteins'
    )
    list_filter = ('meal', 'date')
    search_fields = ('client__user__first_name', 'client__user__last_name', 'plan__name', 'description')

    def client_full_name(self, obj):
        if obj.client and obj.client.user:
            return obj.client.user.get_full_name()
        return "-"

    client_full_name.short_description = 'Клиент'

    def plan_name(self, obj):
        return obj.plan.name if obj.plan else "-"

    plan_name.short_description = 'Хранителен план'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'calories_per_100g',
        'carbohydrates_per_100g',
        'fats_per_100g',
        'proteins_per_100g',
        'serving_size',
    )
    search_fields = ('name',)
    list_filter = ('serving_size',)


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = (
        'meal_display',
        'product',
        'quantity',
        'get_calories',
        'get_carbohydrates',
        'get_fats',
        'get_proteins',
    )
    search_fields = ('product__name', 'meal__description', 'meal__plan__name')
    list_filter = ('meal__meal',)

    def meal_display(self, obj):
        return f"{obj.meal.meal} - {obj.meal.date}"

    meal_display.short_description = 'Хранене'

    def meal_display(self, obj):
        return f"{obj.meal.meal} - {obj.meal.date}"

    meal_display.short_description = 'Хранене'

    def get_calories(self, obj):
        return obj.get_calories()

    get_calories.short_description = 'Калории'

    def get_carbohydrates(self, obj):
        return obj.get_carbohydrates()

    get_carbohydrates.short_description = 'Въглехидрати'

    def get_fats(self, obj):
        return obj.get_fats()

    get_fats.short_description = 'Мазнини'

    def get_proteins(self, obj):
        return obj.get_proteins()

    get_proteins.short_description = 'Протеини'
