import csv
import os
from django.core.management.base import BaseCommand

from fitness_app.meals.models import Product


class Command(BaseCommand):
    help = 'Импортира само продуктите с български имена (от 3-та колона на CSV).'

    def handle(self, *args, **kwargs):
        file_path = os.path.join('fitness_app', 'meals', 'data', 'products.csv')

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')

            count = 0
            for row in reader:
                if len(row) < 3:
                    continue

                bulgarian_name = row[2].strip()

                if not bulgarian_name:
                    continue

                Product.objects.create(
                    name=bulgarian_name[:255],
                    calories=0,
                    protein=0,
                    fat=0,
                    carbohydrates=0,
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Успешно импортирани {count} продукта с български имена.'))
