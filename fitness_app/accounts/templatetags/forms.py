from django import template

register = template.Library()


@register.filter
def placeholder(form_field, text):
    form_field.field.widget.attrs['placeholder'] = text
    return form_field


@register.filter
def form_field_class(form_field, className):
    default_class = form_field.field.widget.attrs.get('class', '')
    form_field.field.widget.attrs['class'] = default_class + ' ' + className
    return form_field

