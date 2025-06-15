from django.contrib import admin
from .models import Workout, WorkoutExercise


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = (
        'program_name',
        'category',
        'description_short',
    )
    list_filter = ('category',)
    search_fields = ('program_name', 'description')

    def description_short(self, obj):
        return (obj.description[:50] + '...') if obj.description and len(obj.description) > 50 else obj.description
    description_short.short_description = 'Описание'


@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    list_display = (
        'workout',
        'exercise',
        'series',
        'repetitions',
        'rest_time',
    )
    list_filter = ('workout__category', 'exercise__name')
    search_fields = ('workout__program_name', 'exercise__name')
