# Generated by Django 5.2 on 2025-05-12 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meal',
            name='meal',
            field=models.CharField(choices=[('Закуска', 'Закуска'), ('Обяд', 'Обяд'), ('Вечеря', 'Вечеря'), ('Снакс / междинно хранене', 'Снакс / междинно хранене')], max_length=24),
        ),
    ]
