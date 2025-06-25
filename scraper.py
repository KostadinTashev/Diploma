import csv
import os
import sys
import django

csv.field_size_limit(2**31 - 1)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fitness_app.settings")
django.setup()

from fitness_app.meals.models import Product

file_path = r"C:\Users\Lenovo\Diploma\fitness_app\en.openfoodfacts.org.products.csv"

def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0

Product.objects.all().delete()

with open(file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile, delimiter='\t')
    count = 0

    for row in reader:
        countries = row.get("countries_tags", "").lower()
        name = row.get("product_name", "").strip()

        if "en:bulgaria" in countries and name:
            if Product.objects.filter(name=name).exists():
                print(f"⏭ Пропуснат (дублиран): {name}")
                continue

            try:
                calories = safe_float(row.get("energy-kcal_100g"))
                carbs = safe_float(row.get("carbohydrates_100g"))
                fats = safe_float(row.get("fat_100g"))
                proteins = safe_float(row.get("proteins_100g"))
                serving = row.get("serving_size", "").strip() or None

                Product.objects.create(
                    name=name,
                    calories_per_100g=calories,
                    carbohydrates_per_100g=carbs,
                    fats_per_100g=fats,
                    proteins_per_100g=proteins,
                    serving_size=serving,
                )
                count += 1
                print(f"✔ Добавен: {name}")

            except Exception as e:
                print(f"⚠ Грешка при {name}: {e}")

print(f"\n✅ Общо добавени продукти: {count}")
