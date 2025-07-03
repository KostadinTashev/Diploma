from collections import defaultdict
from datetime import date
import logging

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.forms import formset_factory
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect

from django.shortcuts import render
from django.utils.timezone import now
from django.views.decorators.http import require_POST

from .forms import FoodItemForm, MealForm, ItemFormSet, MealEntryForm, FoodItemEntryForm, FoodItemAddForm, ProductForm
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


@login_required
def meal_history(request, client_id=None):
    is_trainer = False
    trainer_id = None

    if client_id:
        if not hasattr(request.user, 'trainer'):
            return HttpResponseForbidden("Нямате достъп до тази страница.")
        is_trainer = True
        trainer_id = request.user.trainer.id
        client = get_object_or_404(Client, id=client_id)
    else:
        client = request.user.client

    selected_date_str = request.GET.get('date')
    selected_date = date.fromisoformat(selected_date_str) if selected_date_str else date.today()

    meals = Meal.objects.filter(client=client, date=selected_date).prefetch_related('food_items__product')

    grouped_meals = defaultdict(list)
    for meal in meals:
        key = (meal.meal, meal.date)
        grouped_meals[key].append(meal)

    grouped_totals = {
        key: {
            'calories': sum(m.calories for m in meal_list),
            'carbs': sum(m.carbohydrate for m in meal_list),
            'fats': sum(m.fats for m in meal_list),
            'proteins': sum(m.proteins for m in meal_list),
        }
        for key, meal_list in grouped_meals.items()
    }

    return render(request, 'meals/meal_history.html', {
        'client': client,
        'grouped_meals': dict(grouped_meals),
        'grouped_totals': grouped_totals,
        'selected_date': selected_date.isoformat(),
        'is_trainer': is_trainer,
        'trainer_id': trainer_id,
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


@login_required
def product_list(request):
    q = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "name")  # по подразбиране сортираме по име
    allowed_sort = {
        "name": "name",
        "-name": "-name",
        "cal": "calories_per_100g",
        "-cal": "-calories_per_100g",
        "pro": "proteins_per_100g",
        "-pro": "-proteins_per_100g",
        "carb": "carbohydrates_per_100g",
        "-carb": "-carbohydrates_per_100g",
        "fat": "fats_per_100g",
        "-fat": "-fats_per_100g",
    }
    order_clause = allowed_sort.get(sort, "name")  # fallback

    qs = Product.objects.all()
    if q:
        qs = qs.filter(name__icontains=q)

    products = qs.order_by(order_clause)

    paginator = Paginator(products, 100)  # 100 на страница
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "products": page_obj,  # съдържа само текущата страница
        "page_obj": page_obj,
        "sort": sort,
        "q": q,
    }
    return render(request, "meals/product_list.html", context)


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    client = getattr(request.user, "client", None)
    trainer = getattr(request.user, "trainer", None)

    can_manage = (
            request.user.is_staff
            or request.user.is_superuser
            or trainer is not None
    )

    context = {
        "product": product,
        "client": client,
        "trainer": trainer,
        "can_manage": can_manage,
    }
    return render(request, "meals/product_detail.html", context)


@login_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("product list")
    else:
        form = ProductForm()
    return render(request, "meals/product_create.html", {"form": form})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("product detail", pk=pk)
    else:
        form = ProductForm(instance=product)
    return render(request, "meals/product_edit.html", {"form": form, "product": product})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        return redirect("product list")
    return render(request, "meals/product_confirm_delete.html", {"product": product})
