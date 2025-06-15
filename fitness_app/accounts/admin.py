from django.contrib import admin
from django.contrib.auth import get_user_model

UserModel = get_user_model()


@admin.register(UserModel)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'gender', 'email', 'created_at', 'profile_picture', 'is_staff',)
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    def full_name(self, obj):
        return obj.get_full_name()

    full_name.short_description = 'Пълно име'
