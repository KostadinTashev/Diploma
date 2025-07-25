# Generated by Django 5.2 on 2025-07-03 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exercises', '0003_alter_exercise_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exercise',
            name='category',
            field=models.CharField(blank=True, choices=[('Гърди', 'Гърди'), ('Гръб', 'Гръб'), ('Рамо', 'Рамо'), ('Трицепс', 'Трицепс'), ('Крака', 'Крака'), ('Корем', 'Корем'), ('Кардио', 'Кардио'), ('Функционални', 'Функционални'), ('Аеробика', 'Аеробика'), ('Йога', 'Йога'), ('Пилатес', 'Пилатес')], max_length=12, null=True, verbose_name='Категория'),
        ),
    ]
