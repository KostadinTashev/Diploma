from django.contrib import admin
from .models import ProgramExercise


@admin.register(ProgramExercise)
class ProgramExerciseAdmin(admin.ModelAdmin):
    list_display = ('client_full_name', 'workout_name', 'date')
    list_filter = ('date', 'workout__program_name')
    search_fields = ('client__user__first_name', 'client__user__last_name', 'workout__program_name')

    def client_full_name(self, obj):
        if obj.client and obj.client.user:
            return obj.client.user.get_full_name()
        return "-"
    client_full_name.short_description = 'Клиент'

    def workout_name(self, obj):
        return obj.workout.program_name if obj.workout else "-"
    workout_name.short_description = 'Тренировка'
