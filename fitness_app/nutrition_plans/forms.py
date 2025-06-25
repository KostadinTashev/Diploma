from django import forms
from django.forms import modelformset_factory, inlineformset_factory, modelform_factory

from fitness_app.meals.models import Meal, FoodItem, Product
from fitness_app.nutrition_plans.models import NutritionPlan


class NutritionPlanForm(forms.ModelForm):
    class Meta:
        model = NutritionPlan
        exclude = ['client']


NutritionPlanAddForm = modelform_factory(NutritionPlan, exclude=('client',))


class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        exclude = ['plan']


MealFormAddSet = modelformset_factory(Meal, exclude=('plan', 'client', 'calories', 'carbohydrate', 'fats', 'proteins'),
                                      extra=0, can_delete=True)

MealFormSet = modelformset_factory(Meal, form=MealForm, extra=3, can_delete=True)


class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ['product', 'quantity']


FoodItemFormSet = inlineformset_factory(
    parent_model=Meal,
    model=FoodItem,
    form=FoodItemForm,
    extra=2,
    can_delete=True,
)


class FoodItemNutriForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ['id', 'product', 'quantity']
        widgets = {
            'id': forms.HiddenInput(),
            'product': forms.TextInput(attrs={
                'class': 'product-input',
                'placeholder': 'Име на продукт'
            }),
            'quantity': forms.NumberInput(attrs={
                'placeholder': 'Количество (гр)'
            }),
        }


FoodItemFormAddSet = inlineformset_factory(
    Meal,
    FoodItem,
    form=FoodItemNutriForm,
    fields=('product', 'quantity'),
    extra=0,
    can_delete=True
)


class NutritionPlanEditForm(forms.ModelForm):
    class Meta:
        model = NutritionPlan
        fields = ['name', 'description', 'calories', 'carbohydrate', 'fats', 'proteins']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class MealEditForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['meal', 'date', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }


class FoodItemEditForm(forms.ModelForm):
    product_name = forms.CharField(
        required=False,
        label='Продукт',
        widget=forms.TextInput(attrs={'class': 'autocomplete-product'})
    )

    class Meta:
        model = FoodItem
        fields = ['id', 'product', 'product_name', 'quantity']
        widgets = {
            'id': forms.HiddenInput(),
            'product': forms.HiddenInput(),
            'quantity': forms.NumberInput(attrs={'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.product_id:
            self.fields['product_name'].initial = self.instance.product.name

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        product_name = cleaned_data.get('product_name')

        if product and product_name:
            # ако потребителят е променил името, а ID-то си остава — това е несъответствие
            if product.name.strip().lower() != product_name.strip().lower():
                # създаваме/взимаме нов продукт
                product_obj, _ = Product.objects.get_or_create(name=product_name.strip())
                cleaned_data['product'] = product_obj

        elif product_name and not product:
            # autocomplete не е избран, но име има
            product_obj, _ = Product.objects.get_or_create(name=product_name.strip())
            cleaned_data['product'] = product_obj

        if not cleaned_data.get('product'):
            self.add_error('product_name', 'Моля, изберете или въведете валиден продукт.')

        return cleaned_data



MealFormEditSet = inlineformset_factory(
    NutritionPlan,
    Meal,
    form=MealEditForm,
    extra=0,
    can_delete=True
)

FoodFormEditSet = inlineformset_factory(
    Meal,
    FoodItem,
    form=FoodItemEditForm,
    extra=0,
    can_delete=True
)
