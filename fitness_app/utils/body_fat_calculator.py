import math

def calculate_body_fat_percentage(gender, height, neck, waist, hip=None):
    if gender == 'Мъж':
        return round(86.010 * math.log10(waist - neck) - 70.041 * math.log10(height) + 36.76, 2)
    elif gender == 'Жена' and hip is not None:
        return round(163.205 * math.log10(waist + hip - neck) - 97.684 * math.log10(height) - 78.387, 2)
    return None