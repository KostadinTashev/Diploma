from django.contrib import admin

from fitness_app.trainers.models import Trainer


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'email',
        'gender',
        'speciality',
        'years_of_experience',
        'certifications',
        # 'bio',
        'phone_number',
    )
    search_fields = ('speciality', 'years_of_experience', 'certifications', 'phone_number',)
    ordering = ('speciality', 'years_of_experience', 'certifications', 'phone_number',)
    list_filter = ('speciality', 'years_of_experience', 'certifications', 'phone_number',)

    def full_name(self, obj):
        return obj.user.get_full_name()

    full_name.short_description = "Пълно име"

    def email(self, obj):
        return obj.user.email

    email.short_description = "Имейл"

    def gender(self, obj):
        return obj.user.gender

    gender.short_description = "Пол"
