# Generated by Django 5.2 on 2025-06-17 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workouts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workout',
            name='category',
            field=models.CharField(choices=[('Силова тренировка', 'Силова тренировка'), ('Функционална тренировка', 'Функционална тренировка'), ('Кардио тренировка', 'Кардио тренировка'), ('Аеробна тренировка', 'Аеробна тренировка'), ('HIIT (високоинтензивна интервална)', 'HIIT (високоинтензивна интервална)'), ('Йога', 'Йога'), ('Пилатес', 'Пилатес'), ('Цяло тяло', 'Цяло тяло')], max_length=34, verbose_name='Категория'),
        ),
    ]
