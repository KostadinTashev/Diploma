from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def translate_day(day):
    translations = {
        'Monday': 'Понеделник',
        'Mon': 'Понеделник',
        'Tuesday': 'Вторник',
        'Tue': 'Вторник',
        'Wednesday': 'Сряда',
        'Wed': 'Сряда',
        'Thursday': 'Четвъртък',
        'Thu': 'Четвъртък',
        'Friday': 'Петък',
        'Fri': 'Петък',
        'Saturday': 'Събота',
        'Sat': 'Събота',
        'Sunday': 'Неделя',
        'Sun': 'Неделя',
    }
    return translations.get(day, day)
