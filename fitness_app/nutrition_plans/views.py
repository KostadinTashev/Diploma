from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import modelform_factory, modelformset_factory, inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from fitness_app.clients.models import Client
from fitness_app.meals.models import Product, Meal, FoodItem
from fitness_app.nutrition_plans.forms import FoodItemForm, FoodItemNutriForm, MealForm, MealEditForm, FoodFormEditSet, \
    MealFormEditSet, NutritionPlanEditForm, NutritionPlanForm, NutritionPlanAddForm, MealFormAddSet, FoodItemFormAddSet, \
    FoodItemEditForm
# from fitness_app.nutrition_plans.forms import NutritionPlanForm, FoodItemFormSet, MealFormSet, MealForm
from fitness_app.nutrition_plans.models import NutritionPlan


def plans(request):
    return None


def autocomplete_products(request):
    term = request.GET.get('term', '')
    products = Product.objects.filter(name__icontains=term)[:10]
    results = [{'id': p.id, 'name': p.name} for p in products]
    return JsonResponse(results, safe=False)


@require_http_methods(["GET", "POST"])
def create_nutrition_plan(request, client_id):
    client = get_object_or_404(Client, pk=client_id)

    if request.method == 'POST':
        plan_form = NutritionPlanAddForm(request.POST)
        meal_formset = MealFormAddSet(request.POST, prefix='meals')

        food_formsets = []
        valid = plan_form.is_valid() and meal_formset.is_valid()

        for i, meal_form in enumerate(meal_formset):
            prefix = f'foods-{i}'
            if meal_form.instance.pk:
                food_formset = FoodItemFormAddSet(request.POST, prefix=prefix, instance=meal_form.instance)
            else:
                food_formset = FoodItemFormAddSet(request.POST, prefix=prefix)
            food_formsets.append(food_formset)
            if not food_formset.is_valid():
                valid = False
        if not valid:
            print("Plan form errors:", plan_form.errors)
            print("Meal formset errors:", meal_formset.errors)
            for i, ff in enumerate(food_formsets):
                print(f"Food formset {i} errors:", ff.errors)
        if valid:
            nutrition_plan = plan_form.save(commit=False)
            nutrition_plan.client = client
            nutrition_plan.save()

            meals = meal_formset.save(commit=False)
            for i, meal in enumerate(meals):
                meal.plan = nutrition_plan
                meal.save()
                food_formsets[i].instance = meal
                food_formsets[i].save()

            return redirect('trainer nutrition clients')
    else:
        plan_form = NutritionPlanAddForm()
        meal_formset = MealFormAddSet(queryset=Meal.objects.none(), prefix='meals')

        food_formsets = [FoodItemFormAddSet(prefix='foods-0', queryset=FoodItem.objects.none())]

    context = {
        'client': client,
        'plan_form': plan_form,
        'meal_formset': meal_formset,
        'food_formsets': food_formsets,
        'empty_meal_form': MealFormAddSet(queryset=Meal.objects.none(), prefix='meals').empty_form,
        'empty_food_formset': FoodItemFormAddSet(prefix='foods-__prefix__', queryset=FoodItem.objects.none()),
    }
    return render(request, 'nutrition_plans/plan_add.html', context)


def plan_add(request):
    return None


def plan_details(request, pk):
    plan = get_object_or_404(NutritionPlan, pk=pk)
    meals_by_day = {}

    for meal in plan.meals.all().order_by('date'):
        meal_products = meal.food_items.all()
        formatted_date = meal.date.strftime("%d %B %Y")
        meals_by_day.setdefault(formatted_date, []).append({
            "meal": meal.meal,
            "description": meal.description,
            "calories": meal.calories,
            "carbohydrate": meal.carbohydrate,
            "fats": meal.fats,
            "proteins": meal.proteins,
            "products": meal_products
        })

    return render(request, 'nutrition_plans/plan_details.html', {
        'plan': plan,
        'meals_by_day': meals_by_day,
    })


def plan_delete(request, pk):
    plan = get_object_or_404(NutritionPlan, pk=pk)
    if request.method == "POST":
        plan.delete()
        return redirect('trainer nutrition clients')
    return render(request, 'nutrition_plans/plan_delete.html', {'plan': plan})


@require_http_methods(["GET", "POST"])
def plan_edit(request, plan_id):
    plan = get_object_or_404(NutritionPlan, id=plan_id)
    MealFormSet = inlineformset_factory(NutritionPlan, Meal, form=MealEditForm, extra=0, can_delete=True)
    FoodItemFormSet = inlineformset_factory(Meal, FoodItem, form=FoodItemEditForm, extra=0, can_delete=True)

    if request.method == "POST":
        print("\n\n========== POST DEBUG ==========")
        print("POST KEYS:")
        for key in request.POST.keys():
            print(f" - {key}: {request.POST.getlist(key)}")

        print("\nTrying to initialize forms...")

        plan_form = NutritionPlanForm(request.POST, instance=plan)
        meal_formset = MealFormEditSet(request.POST, instance=plan)

        food_formsets = []
        valid = plan_form.is_valid() and meal_formset.is_valid()
        print(f"Plan form valid: {plan_form.is_valid()}, errors: {plan_form.errors}")
        print(f"Meal formset valid: {meal_formset.is_valid()}, errors: {meal_formset.errors}")

        for meal_form in meal_formset.forms:
            meal_instance = meal_form.instance
            suffix = meal_form.prefix.split('-')[-1]
            prefix = f"foods-{suffix}"
            print(f"\nProcessing food_formset for meal prefix {meal_form.prefix} -> food prefix: {prefix}")

            food_formset = FoodFormEditSet(request.POST, instance=meal_instance, prefix=prefix)
            food_formsets.append(food_formset)

            print(f"Food formset valid: {food_formset.is_valid()}, total forms: {len(food_formset.forms)}")
            if not food_formset.is_valid():
                for form in food_formset.forms:
                    print(f"  Errors in form {form.prefix}: {form.errors}")
                valid = False

        if valid:
            print("\nAll forms valid. Saving...")
            plan_form.save()
            meal_formset.save()

            for food_formset in food_formsets:
                food_items = food_formset.save(commit=False)

                for food_item in food_items:
                    print(f"Saving food item: {food_item}")
                    if not food_item.product:
                        print("  Skipping - product is None")
                        continue
                    food_item.save()

                for deleted in food_formset.deleted_objects:
                    print(f"Deleting food item: {deleted}")
                    deleted.delete()

            messages.success(request, "Хранителният режим беше успешно редактиран.")
            return redirect('plan details', pk=plan.id)
        else:
            print("Form validation failed.")

    else:
        print("GET request - loading existing data")
        plan_form = NutritionPlanForm(instance=plan)
        meal_formset = MealFormSet(instance=plan)

        food_formsets = []
        for idx, meal_form in enumerate(meal_formset.forms):
            meal_instance = meal_form.instance
            prefix = f"foods-{idx}"
            print(f"Creating food_formset with prefix: {prefix}")
            food_formset = FoodItemFormSet(instance=meal_instance, prefix=prefix)
            food_formsets.append(food_formset)
    meals_by_date = defaultdict(list)
    food_formsets_by_meal = {}

    for i, meal_form in enumerate(meal_formset):
        date = meal_form.initial.get("date") or meal_form['date'].value()
        meals_by_date[date].append((i, meal_form))
        food_formsets_by_meal[i] = food_formsets[i]
    context = {
        'plan_form': plan_form,
        'meal_formset': meal_formset,
        'food_formsets': food_formsets,
        "meals_by_date": meals_by_date,
        "food_formsets_by_meal": food_formsets_by_meal,
        'client': plan.client,
        'empty_meal_form': MealFormAddSet(queryset=Meal.objects.none(), prefix='meals').empty_form,
        'empty_food_formset': FoodItemFormAddSet(prefix="foods-__prefix__", queryset=FoodItem.objects.none()),
    }
    return render(request, 'nutrition_plans/plan_edit.html', context)


# def plan_delete(request):
#     return None

def nutrition_plan_day_detail(request, plan_id, day):
    plan = get_object_or_404(NutritionPlan, pk=plan_id)
    meals = plan.meals.filter(day=day)

    context = {
        'plan': plan,
        'day': day,
        'meals': meals,
    }
    return render(request, 'nutrition_plans/nutrition_plan_day_detail.html', context)
