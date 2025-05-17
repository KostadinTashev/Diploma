from django.urls import path, include
from .views import all_meals, meal_add, meal_details, meal_edit, meal_delete

urlpatterns = [
    path('',all_meals, name='all meals'),
    path('add/', meal_add, name='meal add'),
    path('<str:meal_name>', include([
        path('', meal_details, name='meal details'),
        path('edit/', meal_edit, name='meal edit'),
        path('delete/', meal_delete, name='meal delete'),
    ]))
]
