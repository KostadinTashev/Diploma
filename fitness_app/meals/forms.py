from django import forms
from django.forms import formset_factory, inlineformset_factory

from fitness_app.meals.models import FoodItem, Meal, MealType, Product


class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['plan', 'meal', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class FoodItemForm(forms.ModelForm):
    product_name = forms.CharField(label="Продукт", widget=forms.TextInput(attrs={'class': 'autocomplete-input'}))

    class Meta:
        model = FoodItem
        fields = ('product_name', 'quantity')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.product_id:
            self.fields['product_name'].initial = self.instance.product.name

    def clean(self):
        cleaned_data = super().clean()
        product_name = cleaned_data.get('product_name')
        from .models import Product
        products = Product.objects.filter(name__iexact=product_name)
        if not products.exists():
            raise forms.ValidationError(f"Продукт с име '{product_name}' не съществува.")
        product = products.first()
        cleaned_data['product'] = product
        self.instance.product = product
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.product = self.cleaned_data['product']
        if commit:
            instance.save()
        return instance


# class FoodItemForm(forms.Form):
#     product = forms.ModelChoiceField(queryset=Product.objects.all(), label="Продукт")
#     quantity = forms.FloatField(label="Количество (в грамове)")


FoodItemFormSet = formset_factory(FoodItemForm, extra=3)
ItemFormSet = inlineformset_factory(
    Meal,
    FoodItem,
    form=FoodItemForm,
    fields=('product_name', 'quantity'),
    extra=1,
    can_delete=True
)


class SimpleFoodItemForm(forms.Form):
    product_name = forms.CharField(label='Име на продукт')
    quantity = forms.FloatField(label='Количество (в грамове)')


SimpleFoodItemFormSet = formset_factory(SimpleFoodItemForm, extra=3, can_delete=True)


class MealInfoForm(forms.Form):
    date = forms.DateField(widget=forms.SelectDateWidget)
    meal_type = forms.ChoiceField(choices=MealType.choices)


class MealEntryForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['date', 'meal']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }


class FoodItemEntryForm(forms.Form):
    product_name = forms.CharField(label="Продукт", widget=forms.TextInput(attrs={'class': 'autocomplete-input'}))
    quantity = forms.FloatField(label="Количество (г)")

    def clean_product_name(self):
        name = self.cleaned_data['product_name']
        product = Product.objects.filter(name__iexact=name).first()
        if not product:
            raise forms.ValidationError("Невалиден продукт.")
        return product


class FoodItemAddForm(forms.Form):
    product_name = forms.CharField(label="Продукт", widget=forms.TextInput(attrs={'class': 'autocomplete-input'}))
    quantity = forms.FloatField(label="Количество (г)")

    def clean_product_name(self):
        name = self.cleaned_data['product_name']
        if not Product.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("Невалиден продукт.")
        return name
