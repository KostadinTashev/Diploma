from django.contrib import admin
from .models import NutritionPlan
from fitness_app.meals.models import Meal


class MealInline(admin.TabularInline):
    model = Meal
    extra = 1
    readonly_fields = ('calories', 'carbohydrate', 'fats', 'proteins')
    show_change_link = True


@admin.register(NutritionPlan)
class NutritionPlanAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'client_full_name',
        'calories',
        'carbohydrate',
        'fats',
        'proteins',
        'total_meals',
        'total_calories_display',
    )
    search_fields = ('name', 'client__user__first_name', 'client__user__last_name')
    list_filter = ('client__user__gender',)
    inlines = [MealInline]

    def client_full_name(self, obj):
        return obj.client.user.get_full_name() if obj.client and obj.client.user else "-"
    client_full_name.short_description = 'Клиент'

    def total_meals(self, obj):
        return obj.meals.count()
    total_meals.short_description = 'Брой хранения'

    def total_calories_display(self, obj):
        return obj.total_calories()
    total_calories_display.short_description = 'Общо калории от хранения'
