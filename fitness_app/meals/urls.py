from django.urls import path, include
from .views import all_meals, meal_add, meal_details, meal_edit, meal_delete, calorie_calculator, meal_history, \
    edit_meal_client, delete_meal_client

from django.urls import path

from ..nutrition_plans.views import autocomplete_products

urlpatterns = [
    path('', all_meals, name='all meals'),
    path('add/', meal_add, name='meal add'),
    path('calorie-calculator/', calorie_calculator, name='calorie calculator'),
path('meals/history/', meal_history, name='meal history'),
    path('meals/history/<int:client_id>/', meal_history, name='meal history'),
    path('autocomplete-products/', autocomplete_products, name='autocomplete products'),
path('meal/<int:meal_id>/edit/', edit_meal_client, name='edit meal client' ),
    path('meal/<int:meal_id>/delete/', delete_meal_client, name='delete meal client'),
    path('<int:pk>/', include([
        path('', meal_details, name='meal details'),
        path('edit/', meal_edit, name='meal edit'),
        path('delete/', meal_delete, name='meal delete'),
    ])),
]
