from django.contrib import admin

from fitness_app.clients.models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'email',
        'trainer',
        'goals',

    )
    list_filter = ('goals', 'trainer')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')

    def full_name(self, obj):
        return obj.user.get_full_name()

    full_name.short_description = 'Пълно име'

    def email(self, obj):
        return obj.user.email

    email.short_description = 'Имейл'
