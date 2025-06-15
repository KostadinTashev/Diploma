import csv
import os
import sys
import django

csv.field_size_limit(2**31 - 1)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fitness_app.settings")

django.setup()

from fitness_app.meals.models import Product

file_path = r"C:\Users\Lenovo\Diploma\fitness_app\en.openfoodfacts.org.products.csv"

Product.objects.all().delete()
print("Изтрити са всички текущи продукти.")

with open(file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile, delimiter='\t')

    count = 0
    for row in reader:
        countries = row.get("countries_tags", "").lower()
        name = row.get("product_name", "").strip()

        if "en:bulgaria" in countries and name:
            try:
                calories = float(row.get("energy-kcal_100g", "") or 0)
                carbs = float(row.get("carbohydrates_100g", "") or 0)
                fats = float(row.get("fat_100g", "") or 0)
                proteins = float(row.get("proteins_100g", "") or 0)
                serving = row.get("serving_size", "").strip()

                product = Product.objects.create(
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
                print(f"Грешка при {name}: {e}")

print(f"\nОбщо добавени продукти: {count}")
