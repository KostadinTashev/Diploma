from django.contrib import admin

from fitness_app.exercises.models import Exercise, CompletedExercise


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'equipment', 'has_picture')
    list_filter = ('category',)
    search_fields = ('name', 'description', 'equipment')

    def has_picture(self, obj):
        return bool(obj.exercise_picture)

    has_picture.boolean = True
    has_picture.short_description = 'Снимка'


@admin.register(CompletedExercise)
class CompletedExerciseAdmin(admin.ModelAdmin):
    list_display = ('client_full_name', 'exercise_name', 'workout_name', 'date')
    list_filter = ('date', 'workout_exercise__exercise__category')
    search_fields = (
        'client__user__first_name',
        'client__user__last_name',
        'workout_exercise__exercise__name',
        'workout_exercise__workout__program_name',
    )

    def client_full_name(self, obj):
        return obj.client.user.get_full_name()
    client_full_name.short_description = 'Клиент'

    def exercise_name(self, obj):
        return obj.workout_exercise.exercise.name
    exercise_name.short_description = 'Упражнение'

    def workout_name(self, obj):
        return obj.workout_exercise.workout.program_name
    workout_name.short_description = 'Тренировка'
