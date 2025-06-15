from django.contrib import admin
from .models import Progress


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = (
        'client_full_name',
        'progress_date',
        'weight',
        'height',
        'weight',
        'waist',
        'hip',
        'body_fat_percentage',
        'muscle_mass',
    )
    list_filter = ('progress_date', 'client__user__first_name')
    search_fields = (
        'client__user__first_name',
        'client__user__last_name',
    )

    def client_full_name(self, obj):
        if obj.client and obj.client.user:
            return obj.client.user.get_full_name()
        return "-"

    client_full_name.short_description = 'Клиент'
