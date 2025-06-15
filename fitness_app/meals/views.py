from collections import defaultdict
from datetime import date
import logging
from django.forms import formset_factory
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect

from django.shortcuts import render
from django.utils.timezone import now
from django.views.decorators.http import require_POST

from .forms import FoodItemForm, MealForm, ItemFormSet, MealEntryForm, FoodItemEntryForm, FoodItemAddForm
from .models import Meal, FoodItem, Product
from ..clients.models import Client


def calorie_calculator(request):
    FoodItemFormSet = formset_factory(FoodItemAddForm, extra=1)
    client = request.user.client
    nutrition_plan = client.nutrition_plans.last()

    if request.method == 'POST':
        meal_form = MealEntryForm(request.POST)
        formset = FoodItemFormSet(request.POST)

        if meal_form.is_valid() and formset.is_valid():
            meal = meal_form.save(commit=False)
            meal.client = client
            meal.calories = 0
            meal.carbohydrate = 0
            meal.fats = 0
            meal.proteins = 0
            meal.save()

            for i, form in enumerate(formset):
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    product_name = form.cleaned_data['product_name']
                    quantity = form.cleaned_data['quantity']


                    products = Product.objects.filter(name__iexact=product_name)
                    count = products.count()

                    if not products.exists():
                        continue

                    if count > 1:
                        for p in products:
                            print(f"  - Product ID: {p.id}, Name: {p.name}")
                        product = products.order_by('id').first()
                    else:
                        product = products.first()

                    food_item = FoodItem.objects.create(
                        meal=meal,
                        product=product,
                        quantity=quantity
                    )

                    meal.calories += food_item.get_calories()
                    meal.carbohydrate += food_item.get_carbohydrates()
                    meal.fats += food_item.get_fats()
                    meal.proteins += food_item.get_proteins()

            meal.save()

            return redirect('calorie calculator')

    else:
        meal_form = MealEntryForm(initial={'date': now().date()})
        formset = FoodItemFormSet()

    today = now().date()
    meals_today = Meal.objects.filter(client=client, date=today).order_by('meal')

    grouped_meals = defaultdict(list)
    for meal in meals_today:
        grouped_meals[meal.get_meal_display()].append(meal)
    grouped_meals = dict(grouped_meals)

    grouped_food_items = defaultdict(list)
    for meal_type, meals in grouped_meals.items():
        all_food_items = []
        for meal in meals:
            all_food_items.extend(meal.food_items.all())
        grouped_food_items[meal_type] = all_food_items

    total_calories = sum(m.calories for m in meals_today)
    total_proteins = sum(m.proteins for m in meals_today)
    total_fats = sum(m.fats for m in meals_today)
    total_carbohydrate = sum(m.carbohydrate for m in meals_today)

    if nutrition_plan:
        calories_left = nutrition_plan.calories - total_calories
        proteins_left = nutrition_plan.proteins - total_proteins
        fats_left = nutrition_plan.fats - total_fats
        carbohydrate_left = nutrition_plan.carbohydrate - total_carbohydrate
        plan_name = nutrition_plan.name
    else:
        calories_left = 0
        proteins_left = 0
        fats_left = 0
        carbohydrate_left = 0
        plan_name = "Няма зададен хранителен план"

    context = {
        'meal_form': meal_form,
        'formset': formset,
        'calories_left': calories_left,
        'proteins_left': proteins_left,
        'fats_left': fats_left,
        'carbohydrate_left': carbohydrate_left,
        'meals_today': meals_today,
        'plan_name': plan_name,
        'current_date': today,
        'grouped_meals': grouped_meals,
        'grouped_food_items': grouped_food_items
    }

    return render(request, 'meals/calorie_calculator.html', context)


def meal_history(request, client_id=None):
    if client_id:
        if not request.user.trainer:
            return HttpResponseForbidden("Нямате достъп до тази страница.")
        client = get_object_or_404(Client, id=client_id)
    else:
        client = request.user.client

    selected_date_str = request.GET.get('date')
    if selected_date_str:
        selected_date = date.fromisoformat(selected_date_str)
    else:
        selected_date = date.today()

    meals = Meal.objects.filter(client=client, date=selected_date).prefetch_related('food_items__product')

    grouped_meals = defaultdict(list)
    for meal in meals:
        key = (meal.meal, meal.date)
        grouped_meals[key].append(meal)

    grouped_totals = {}
    for key, meals_list in grouped_meals.items():
        grouped_totals[key] = {
            'calories': sum(m.calories for m in meals_list),
            'carbs': sum(m.carbohydrate for m in meals_list),
            'fats': sum(m.fats for m in meals_list),
            'proteins': sum(m.proteins for m in meals_list),
        }

    return render(request, 'meals/meal_history.html', {
        'client': client,
        'grouped_meals': dict(grouped_meals),
        'grouped_totals': grouped_totals,
        'selected_date': selected_date.isoformat(),
    })


def all_meals(request):
    meals = Meal.objects.all()
    return render(request, 'meals/all_meals.html', {'meals': meals})


def meal_add(request):
    if request.method == 'POST':
        meal_form = MealForm(request.POST)
        formset = ItemFormSet(request.POST)

        if meal_form.is_valid() and formset.is_valid():
            meal = meal_form.save()

            for form in formset:
                if form.cleaned_data:
                    product_name = form.cleaned_data.get('product_name')
                    quantity = form.cleaned_data.get('quantity')

                    if product_name:
                        try:
                            product = Product.objects.get(name__iexact=product_name)
                        except Product.DoesNotExist:
                            form.add_error('product_name', 'Продуктът не съществува.')
                            return render(request, 'meals/meal_add.html', {
                                'meal_form': meal_form,
                                'formset': formset
                            })

                        FoodItem.objects.create(
                            meal=meal,
                            product=product,
                            quantity=quantity
                        )

            return redirect('meals_list')

    else:
        meal_form = MealForm()
        formset = ItemFormSet()

    return render(request, 'meals/meal_add.html', {
        'meal_form': meal_form,
        'formset': formset
    })


def meal_details(request, pk):
    meal = get_object_or_404(Meal, pk=pk)
    return render(request, 'meals/meal_details.html', {'meal': meal})


def meal_edit(request, pk):
    meal = get_object_or_404(Meal, pk=pk)
    if request.method == 'POST':
        form = MealForm(request.POST, instance=meal)
        if form.is_valid():
            form.save()
            return redirect('meal details', pk=meal.pk)
    else:
        form = MealForm(instance=meal)
    return render(request, 'meals/meal_edit.html', {'form': form, 'action': 'Редактирай'})


def edit_meal_client(request, meal_id):
    client = request.user.client
    meal = get_object_or_404(Meal, id=meal_id, client=client)
    FoodItemFormSet = formset_factory(FoodItemEntryForm, extra=0, can_delete=True)

    if request.method == 'POST':

        meal_form = MealEntryForm(request.POST, instance=meal)
        formset = FoodItemFormSet(request.POST)

        if meal_form.is_valid() and formset.is_valid():
            meal = meal_form.save(commit=False)
            meal.client = client

            meal.calories = 0
            meal.carbohydrate = 0
            meal.fats = 0
            meal.proteins = 0
            meal.save()

            meal.food_items.all().delete()

            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    product = form.cleaned_data.get('product_name')
                    quantity = form.cleaned_data.get('quantity')

                    if not isinstance(product, Product):
                        continue

                    food_item = FoodItem.objects.create(
                        meal=meal,
                        product=product,
                        quantity=quantity
                    )

                    meal.calories += food_item.get_calories()
                    meal.carbohydrate += food_item.get_carbohydrates()
                    meal.fats += food_item.get_fats()
                    meal.proteins += food_item.get_proteins()

            meal.save()
            return redirect('calorie calculator')

    else:
        meal_form = MealEntryForm(instance=meal)
        initial_data = [{'product_name': item.product.name, 'quantity': item.quantity} for item in
                        meal.food_items.all()]
        formset = FoodItemFormSet(initial=initial_data)

    context = {
        'meal_form': meal_form,
        'formset': formset,
        'edit_mode': True,
        'meal_id': meal.id,
    }

    return render(request, 'meals/calorie_calculator_edit.html', context)


def meal_delete(request, pk):
    meal = get_object_or_404(Meal, pk=pk)
    if request.method == 'POST':
        meal.delete()
        return redirect('all meals')
    return render(request, 'meals/meal_delete.html', {'meal': meal})


@require_POST
def delete_meal_client(request, meal_id):
    client = request.user.client
    meal = get_object_or_404(Meal, id=meal_id, client=client)
    meal.delete()
    return redirect('calorie calculator')
