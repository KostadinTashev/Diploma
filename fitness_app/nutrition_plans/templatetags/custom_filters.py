from django import template

from fitness_app.meals.models import Product

register = template.Library()

@register.filter
def index(sequence, position):
    try:
        return sequence[position]
    except:
        return None

@register.filter
def get_product_name(product_id):
    if not product_id:
        return ''
    try:
        product = Product.objects.get(pk=product_id)
        return product.name
    except Product.DoesNotExist:
        return ''