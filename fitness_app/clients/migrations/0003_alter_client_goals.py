# Generated by Django 5.2 on 2025-05-12 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0002_client_chest_client_height_client_waist_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='goals',
            field=models.CharField(blank=True, choices=[('Отслабване', 'Отслабване'), ('Мускулна маса', 'Мускулна маса'), ('Здравословно хранене', 'Здравословно хранене'), ('Поддържане на тегло', 'Поддържане на тегло')], max_length=20, null=True),
        ),
    ]
