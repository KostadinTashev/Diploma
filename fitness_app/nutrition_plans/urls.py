from django.urls import path
from .views import (
    plans,
    plan_add,
    plan_details,
    plan_edit,
    plan_delete,
    create_nutrition_plan,
    autocomplete_products,
)

urlpatterns = [
    path('', plans, name='plans'),

    path('autocomplete-products/', autocomplete_products, name='autocomplete products'),

    path('client/<int:client_id>/create/', create_nutrition_plan, name='create nutrition plan'),

    path('<int:pk>/', plan_details, name='plan details'),
    path('<int:plan_id>/edit/', plan_edit, name='plan edit'),
    path('<int:pk>/delete/', plan_delete, name='plan delete'),
]
